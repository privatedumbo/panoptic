from pathlib import Path
from typing import Any

from pydantic import BaseModel


class Document(BaseModel):
    """Parsed document with its extracted text."""

    text: str
    source: Path


class Entity(BaseModel):
    """A single NER mention extracted from text."""

    text: str
    label: str
    confidence: float
    metadata: dict[str, Any]


class WikidataType(BaseModel):
    """A Wikidata type entry (from P31 instance_of)."""

    id: str
    label: str


class KnowledgeBaseRef(BaseModel):
    """Pointer into external knowledge graphs."""

    wikidata_id: str | None = None
    google_kg_id: str | None = None


class ResolvedEntity(BaseModel):
    """A canonical entity anchored to external knowledge graphs."""

    canonical_name: str
    entity_type: str
    mentions: list[str]
    kb_ref: KnowledgeBaseRef = KnowledgeBaseRef()
    instance_of: list[WikidataType] = []


class ResolutionResult(BaseModel):
    """The full resolution output for a text chunk."""

    entities: list[ResolvedEntity]

    def display(self) -> str:
        """Format the result for human-readable output."""
        grouped: dict[str, list[ResolvedEntity]] = {}
        for entity in self.entities:
            grouped.setdefault(entity.entity_type, []).append(entity)

        lines: list[str] = []
        for entity_type, entities in grouped.items():
            lines.append(f"\n{entity_type}")
            lines.append("-" * len(entity_type))
            for e in sorted(entities, key=lambda x: x.canonical_name):
                mentions = ", ".join(e.mentions)
                parts = [f"  {e.canonical_name}: {mentions}"]
                if e.kb_ref.wikidata_id:
                    parts.append(f"    [{e.kb_ref.wikidata_id}]")
                if e.instance_of:
                    type_labels = ", ".join(t.label for t in e.instance_of)
                    parts.append(f"    types: {type_labels}")
                lines.extend(parts)

        return "\n".join(lines)
