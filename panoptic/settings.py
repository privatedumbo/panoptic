"""Application settings loaded from environment variables.

All fields can be overridden via env vars with the ``PANOPTIC_`` prefix.
For example: ``PANOPTIC_LLM_MODEL=groq/llama-3.1-70b-versatile``.
"""

import functools
from pathlib import Path

from pydantic_settings import BaseSettings


class PanopticSettings(BaseSettings):
    """Central configuration for the panoptic pipeline."""

    model_config = {"env_prefix": "PANOPTIC_", "frozen": True}

    # Cache
    cache_dir: Path = Path.home() / ".cache" / "panoptic"

    # NER
    ner_methods: tuple[str, ...] = ("ml", "pattern")
    ner_model: str = "en_core_web_trf"
    ner_min_confidence: float = 0.6
    ner_entity_types: tuple[str, ...] = ("PERSON", "ORG", "GPE")

    # LLM
    llm_model: str = "openai/gpt-4o-mini"


@functools.lru_cache(maxsize=1)
def get_settings() -> PanopticSettings:
    """Return the application settings (cached singleton)."""
    return PanopticSettings()
