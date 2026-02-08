"""Unit tests for panoptic.prompts — prompt construction logic."""

from types import SimpleNamespace
from typing import Any

from panoptic.prompts import build_user_prompt


def _entity(text: str) -> Any:
    """Lightweight stand-in for semantica Entity."""
    return SimpleNamespace(text=text)


class TestBuildUserPrompt:
    """Tests for user prompt assembly."""

    def test_deduplicates_mentions(self) -> None:
        mentions = [_entity("John"), _entity("John"), _entity("Acme")]
        result = build_user_prompt("Some text.", mentions)

        assert result.count('"John"') == 1

    def test_sorts_mentions_alphabetically(self) -> None:
        mentions = [_entity("Zara"), _entity("Acme"), _entity("John")]
        result = build_user_prompt("Some text.", mentions)

        assert result.index('"Acme"') < result.index('"John"') < result.index('"Zara"')

    def test_wraps_text_in_triple_quotes(self) -> None:
        result = build_user_prompt("Hello world.", [_entity("X")])

        assert '"""\nHello world.\n"""' in result

    def test_preserves_unicode_in_mentions(self) -> None:
        result = build_user_prompt("Texte.", [_entity("François")])

        assert "François" in result
