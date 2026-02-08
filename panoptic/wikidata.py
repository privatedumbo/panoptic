"""Wikidata entity linking service.

Enriches resolved entities with Wikidata QIDs and shallow type info
(P31 instance_of) by:
1. Searching Wikidata for each entity via the wbsearchentities API.
2. Batch-disambiguating ambiguous matches with a single LLM call.
3. Fetching instance_of types for all linked QIDs via a single SPARQL query.
"""

import json
import logging
from typing import Any

import httpx
import litellm

from panoptic.models import (
    KnowledgeBaseRef,
    ResolutionResult,
    ResolvedEntity,
    WikidataType,
)
from panoptic.prompts import (
    DISAMBIGUATION_SYSTEM_PROMPT,
    build_disambiguation_prompt,
)
from panoptic.settings import PanopticSettings

logger = logging.getLogger(__name__)

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "panoptic/0.0.1 (https://github.com/fbocci/panoptic)"

MAX_SEARCH_RESULTS = 5


class WikidataLinker:
    """Enrich resolved entities with Wikidata QIDs and type info."""

    def __init__(self, settings: PanopticSettings) -> None:
        self.settings = settings
        self._client = httpx.Client(
            timeout=30.0,
            headers={"User-Agent": USER_AGENT},
        )

    def link(
        self,
        result: ResolutionResult,
        document_text: str,
    ) -> ResolutionResult:
        """Enrich all entities in *result* with Wikidata links and types."""
        if not result.entities:
            return result

        # Step 1: search Wikidata for candidates per entity
        candidates_by_name: dict[str, list[dict[str, str]]] = {}
        for entity in result.entities:
            candidates_by_name[entity.canonical_name] = self._search_entity(
                entity.canonical_name,
            )

        # Step 2: separate unambiguous (single candidate) from ambiguous
        auto_linked: dict[str, str] = {}
        ambiguous: list[dict[str, Any]] = []

        for entity in result.entities:
            candidates = candidates_by_name[entity.canonical_name]
            if len(candidates) == 1:
                auto_linked[entity.canonical_name] = candidates[0]["qid"]
            elif len(candidates) > 1:
                ambiguous.append(
                    {
                        "canonical_name": entity.canonical_name,
                        "entity_type": entity.entity_type,
                        "candidates": candidates,
                    },
                )
            # len == 0 → no match found, entity stays unlinked

        # Step 3: batch LLM disambiguation for ambiguous entities
        llm_linked = (
            self._batch_disambiguate(document_text, result.entities, ambiguous)
            if ambiguous
            else {}
        )

        qid_map = {**auto_linked, **llm_linked}

        # Step 4: fetch type info for all linked QIDs in one SPARQL query
        linked_qids = [qid for qid in qid_map.values() if qid]
        type_info = self._fetch_types(linked_qids) if linked_qids else {}

        # Step 5: build enriched entities
        enriched: list[ResolvedEntity] = []
        for entity in result.entities:
            qid = qid_map.get(entity.canonical_name)
            enriched.append(
                entity.model_copy(
                    update={
                        "kb_ref": KnowledgeBaseRef(wikidata_id=qid),
                        "instance_of": type_info.get(qid, []) if qid else [],
                    },
                ),
            )

        return ResolutionResult(entities=enriched)

    # ------------------------------------------------------------------
    # Wikidata search
    # ------------------------------------------------------------------

    def _search_entity(self, name: str) -> list[dict[str, str]]:
        """Search Wikidata for items matching *name*."""
        params: dict[str, str | int] = {
            "action": "wbsearchentities",
            "search": name,
            "language": self.settings.wikidata_language,
            "format": "json",
            "limit": MAX_SEARCH_RESULTS,
            "type": "item",
        }
        try:
            resp = self._client.get(WIKIDATA_API_URL, params=params)
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.warning("Wikidata search failed for %r", name)
            return []

        data = resp.json()
        return [
            {
                "qid": item["id"],
                "label": item.get("label", ""),
                "description": item.get("description", ""),
            }
            for item in data.get("search", [])
        ]

    # ------------------------------------------------------------------
    # LLM disambiguation
    # ------------------------------------------------------------------

    def _batch_disambiguate(
        self,
        document_text: str,
        all_entities: list[ResolvedEntity],
        ambiguous: list[dict[str, Any]],
    ) -> dict[str, str | None]:
        """Use the LLM to pick the best QID for each ambiguous entity."""
        all_names = [e.canonical_name for e in all_entities]
        user_prompt = build_disambiguation_prompt(
            document_text,
            all_names,
            ambiguous,
        )

        try:
            response: Any = litellm.completion(
                model=self.settings.llm_model,
                messages=[
                    {"role": "system", "content": DISAMBIGUATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            raw: str = response.choices[0].message.content
            data: dict[str, Any] = json.loads(raw)
            links: dict[str, str | None] = data.get("links", {})
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("LLM disambiguation failed, skipping")
            return {}

        # Validate that returned QIDs are actually in the candidate lists
        valid_qids: dict[str, set[str]] = {
            entry["canonical_name"]: {c["qid"] for c in entry["candidates"]}
            for entry in ambiguous
        }

        validated: dict[str, str | None] = {}
        for name, qid in links.items():
            if qid is None:
                validated[name] = None
            elif name in valid_qids and qid in valid_qids[name]:
                validated[name] = qid
            else:
                logger.warning(
                    "LLM returned invalid QID %r for %r, skipping",
                    qid,
                    name,
                )

        return validated

    # ------------------------------------------------------------------
    # SPARQL type fetching
    # ------------------------------------------------------------------

    def _fetch_types(
        self,
        qids: list[str],
    ) -> dict[str, list[WikidataType]]:
        """Fetch P31 (instance_of) types for all *qids* in a single SPARQL query."""
        values = " ".join(f"wd:{qid}" for qid in qids)
        query = f"""
        SELECT ?item ?type ?typeLabel WHERE {{
          VALUES ?item {{ {values} }}
          ?item wdt:P31 ?type .
          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "{self.settings.wikidata_language},en" .
          }}
        }}
        """

        params: dict[str, str] = {"query": query, "format": "json"}
        try:
            resp = self._client.get(
                WIKIDATA_SPARQL_URL,
                params=params,
                headers={"Accept": "application/sparql-results+json"},
            )
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.warning("SPARQL type query failed")
            return {}

        results = resp.json().get("results", {}).get("bindings", [])
        types_by_qid: dict[str, list[WikidataType]] = {}

        for row in results:
            item_uri = row["item"]["value"]
            qid = item_uri.rsplit("/", maxsplit=1)[-1]
            type_uri = row["type"]["value"]
            type_id = type_uri.rsplit("/", maxsplit=1)[-1]
            type_label = row.get("typeLabel", {}).get("value", type_id)

            types_by_qid.setdefault(qid, []).append(
                WikidataType(id=type_id, label=type_label),
            )

        return types_by_qid
