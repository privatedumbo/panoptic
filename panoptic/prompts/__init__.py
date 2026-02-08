"""LLM prompt templates for each pipeline stage."""

from panoptic.prompts.disambiguation import (
    DISAMBIGUATION_SYSTEM_PROMPT,
    build_disambiguation_prompt,
)
from panoptic.prompts.resolution import (
    RESOLUTION_SYSTEM_PROMPT,
    build_resolution_prompt,
)

__all__ = [
    "DISAMBIGUATION_SYSTEM_PROMPT",
    "RESOLUTION_SYSTEM_PROMPT",
    "build_disambiguation_prompt",
    "build_resolution_prompt",
]
