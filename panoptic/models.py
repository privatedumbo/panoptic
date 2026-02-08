from enum import StrEnum
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


class EntityType(StrEnum):
    PERSON = "PERSON"
    ORG = "ORG"
    GPE = "GPE"


class ResolvedEntity(BaseModel):
    """A single canonical entity with all of its surface mentions."""

    canonical_name: str
    entity_type: EntityType
    mentions: list[str]


class ResolutionResult(BaseModel):
    """The full resolution output for a text chunk."""

    entities: list[ResolvedEntity]

    def display(self) -> str:
        """Format the result for human-readable output."""
        grouped: dict[EntityType, list[ResolvedEntity]] = {}
        for entity in self.entities:
            grouped.setdefault(entity.entity_type, []).append(entity)

        lines: list[str] = []
        for entity_type in EntityType:
            entities = grouped.get(entity_type, [])
            if not entities:
                continue
            lines.append(f"\n{entity_type.value}")
            lines.append("-" * len(entity_type.value))
            for e in sorted(entities, key=lambda x: x.canonical_name):
                mentions = ", ".join(e.mentions)
                lines.append(f"  {e.canonical_name}: {mentions}")

        return "\n".join(lines)
