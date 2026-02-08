"""Prompts for Wikidata entity disambiguation via LLM."""

from typing import Any

DISAMBIGUATION_SYSTEM_PROMPT = """\
You are a Wikidata entity linking expert. You will receive:
1. An excerpt from the source document for context.
2. The full list of entities found in the document.
3. A set of ambiguous entities with their Wikidata candidate matches.

Your job is to pick the single best Wikidata item for each ambiguous entity, \
using the document context and co-occurring entities to inform your choice.

Return **only** valid JSON matching this schema — no commentary:

{
  "links": {
    "<canonical_name>": "<QID or null>"
  }
}

Rules:
- Pick the candidate whose description best matches the document context.
- If no candidate is a reasonable match, map the entity to null.
- Do NOT invent QIDs that are not in the candidate lists.
"""

MAX_CONTEXT_LENGTH = 2000


def build_disambiguation_prompt(
    document_text: str,
    all_entity_names: list[str],
    ambiguous_entities: list[dict[str, Any]],
) -> str:
    """Build a user prompt for batched Wikidata disambiguation.

    Args:
        document_text: Full document text (will be truncated for the prompt).
        all_entity_names: Names of all entities in the document, for context.
        ambiguous_entities: Entries with keys canonical_name, entity_type,
            and candidates (list of dicts with qid, label, description).
    """
    excerpt = document_text[:MAX_CONTEXT_LENGTH]
    if len(document_text) > MAX_CONTEXT_LENGTH:
        excerpt += " [...]"

    entity_list = ", ".join(all_entity_names)

    sections: list[str] = []
    for i, entry in enumerate(ambiguous_entities, start=1):
        name = entry["canonical_name"]
        etype = entry["entity_type"]
        candidates = entry["candidates"]
        candidate_lines = "\n".join(
            f"  - {c['qid']}: {c['label']} — {c['description']}" for c in candidates
        )
        sections.append(f"{i}. {name} ({etype})\n   Candidates:\n{candidate_lines}")

    entity_block = "\n\n".join(sections)

    return (
        f'Document excerpt:\n"""\n{excerpt}\n"""\n\n'
        f"All entities in document: {entity_list}\n\n"
        f"Pick the best Wikidata match for each entity:\n\n{entity_block}"
    )
