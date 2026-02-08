"""Unit tests for panoptic.cache — key generation and caching logic."""

import hashlib
from pathlib import Path
from typing import Any
from unittest.mock import patch

from panoptic.cache import _file_hash, _make_key, _serialize_arg, cached


class TestSerializeArg:
    """Tests for argument serialization into cache key segments."""

    def test_plain_value_uses_repr(self) -> None:
        assert _serialize_arg("hello") == "'hello'"
        assert _serialize_arg(42) == "42"

    def test_path_to_existing_file_includes_content_hash(
        self,
        tmp_path: Path,
    ) -> None:
        f = tmp_path / "doc.txt"
        f.write_text("content")
        result = _serialize_arg(f)

        assert result.startswith(f"path:{f.resolve()}:")
        assert result.endswith(_file_hash(f.resolve()))

    def test_path_to_missing_file_includes_missing(self, tmp_path: Path) -> None:
        f = tmp_path / "ghost.txt"
        result = _serialize_arg(f)

        assert result == f"path:{f.resolve()}:missing"


class TestMakeKey:
    """Tests for deterministic cache key construction."""

    def test_kwarg_order_does_not_affect_key(self) -> None:
        key_a = _make_key("fn", (), {"x": 1, "y": 2})
        key_b = _make_key("fn", (), {"y": 2, "x": 1})

        assert key_a == key_b

    def test_different_func_names_produce_different_keys(self) -> None:
        key_a = _make_key("func_a", ("arg",), {})
        key_b = _make_key("func_b", ("arg",), {})

        assert key_a != key_b

    def test_different_args_produce_different_keys(self) -> None:
        key_a = _make_key("fn", (1,), {})
        key_b = _make_key("fn", (2,), {})

        assert key_a != key_b


class TestFileHash:
    """Tests for file content hashing."""

    def test_matches_known_sha256(self, tmp_path: Path) -> None:
        f = tmp_path / "test.bin"
        payload = b"deterministic content"
        f.write_bytes(payload)

        expected = hashlib.sha256(payload).hexdigest()

        assert _file_hash(f) == expected

    def test_different_content_produces_different_hash(self, tmp_path: Path) -> None:
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("version 1")
        b.write_text("version 2")

        assert _file_hash(a) != _file_hash(b)


class TestCachedDecorator:
    """Tests for the @cached disk-caching decorator."""

    def test_second_call_returns_cached_result(self) -> None:
        call_count = 0
        fake_cache: dict[str, Any] = {}

        @cached
        def compute(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        with patch("panoptic.cache._get_cache", return_value=fake_cache):
            first = compute(5)
            second = compute(5)

        assert first == second == 10
        assert call_count == 1

    def test_different_args_are_cached_separately(self) -> None:
        fake_cache: dict[str, Any] = {}

        @cached
        def double(x: int) -> int:
            return x * 2

        with patch("panoptic.cache._get_cache", return_value=fake_cache):
            assert double(3) == 6
            assert double(4) == 8
            assert len(fake_cache) == 2
