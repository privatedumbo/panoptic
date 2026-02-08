import json

from panoptic.models import Entity

SYSTEM_PROMPT = """\
You are an entity resolution expert.  Given a text and a set of named-entity \
mentions extracted by an NER system, your job is to:

1. Identify any additional references to PERSON, ORG, or GPE entities that the \
NER system may have missed — including titles, descriptions, abbreviations, and \
pronouns that clearly refer to a specific entity.
2. Group every mention (extracted + newly identified) that refers to the same \
real-world entity.
3. Choose the best canonical name for each group (prefer the most complete, \
commonly-used proper name).

Return **only** valid JSON matching this schema — no commentary:

{
  "entities": [
    {
      "canonical_name": "<best proper name>",
      "entity_type": "<PERSON | ORG | GPE>",
      "mentions": ["<mention1>", "<mention2>", ...]
    }
  ]
}

Rules:
- entity_type must be one of: PERSON, ORG, GPE.
- Every extracted mention must appear in exactly one group.
- Do NOT invent entities that are not referenced in the text.
- Mentions should be the exact surface forms found in the text.
"""


def build_user_prompt(text: str, mentions: list[Entity]) -> str:
    unique_mentions = sorted({m.text for m in mentions})
    mention_lines = json.dumps(unique_mentions, ensure_ascii=False)
    return f'Text:\n"""\n{text}\n"""\n\nExtracted NER mentions:\n{mention_lines}'
