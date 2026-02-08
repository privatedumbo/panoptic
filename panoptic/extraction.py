"""Named-entity extraction via semantica NER."""

import functools

from semantica.semantic_extract import NERExtractor

from panoptic.models import Document, Entity
from panoptic.settings import PanopticSettings


@functools.lru_cache(maxsize=1)
def _get_extractor(settings: PanopticSettings) -> NERExtractor:
    """Build the NER extractor from current settings (cached)."""
    return NERExtractor(
        method=list(settings.ner_methods),
        entity_types=list(settings.ner_entity_types),
        model=settings.ner_model,
        min_confidence=settings.ner_min_confidence,
    )


class EntityExtractor:
    """Extract named entities from text via semantica NER."""

    def __init__(self, settings: PanopticSettings):
        self.extractor = _get_extractor(settings)

    def extract_entities(self, document: Document) -> list[Entity]:
        """Return NER-detected entities for the given document."""
        entities = self.extractor.extract_entities(document.text)
        return [
            Entity(
                text=entity.text,
                label=entity.label,
                confidence=entity.confidence,
                metadata=entity.metadata,
            )
            for entity in entities
        ]
