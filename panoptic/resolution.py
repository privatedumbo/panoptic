"""LLM-based canonical entity resolution.

Takes raw NER mentions and the source text, then uses an LLM to:
1. Identify additional entity references spaCy missed (titles, descriptions).
2. Group all mentions that refer to the same real-world entity.
3. Return a canonical name for each group.

"""

import json
import logging
from typing import Any

import litellm

from panoptic.models import Document, Entity, ResolutionResult
from panoptic.prompts import RESOLUTION_SYSTEM_PROMPT, build_resolution_prompt
from panoptic.settings import PanopticSettings

logger = logging.getLogger(__name__)


class EntityResolver:
    """Resolve raw NER mentions to canonical entities via LLM."""

    def __init__(self, settings: PanopticSettings):
        self.settings = settings

    def resolve_entities(
        self,
        document: Document,
        mentions: list[Entity],
    ) -> ResolutionResult:
        """Resolve raw NER mentions to canonical entities via LLM."""
        if not mentions:
            return ResolutionResult(entities=[])

        return self._call_llm(document, mentions)

    def _call_llm(
        self,
        document: Document,
        mentions: list[Entity],
    ) -> ResolutionResult:
        """Send the resolution prompt to the configured LLM and parse output."""
        user_prompt = build_resolution_prompt(document.text, mentions)

        response: Any = litellm.completion(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": RESOLUTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        raw: str = response.choices[0].message.content
        data: dict[str, Any] = json.loads(raw)
        return ResolutionResult.model_validate(data)
