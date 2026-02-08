"""Disk-based function result caching with content-aware keys."""

import functools
import hashlib
from pathlib import Path
from typing import Any

import diskcache

from panoptic.settings import get_settings


@functools.lru_cache(maxsize=1)
def _get_cache() -> diskcache.Cache:
    """Return the shared diskcache instance, creating it on first use."""
    # Resolved here so the decorator stays settings-agnostic.
    cache_dir = get_settings().cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    return diskcache.Cache(str(cache_dir))


def _make_key(func_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Build a deterministic cache key from function name and arguments.

    Path arguments are resolved to absolute paths so that equivalent paths
    produce the same key, and file contents are hashed so re-parsing is
    triggered when the underlying file changes.
    """
    parts: list[str] = [func_name]
    parts.extend(_serialize_arg(arg) for arg in args)
    parts.extend(f"{k}={_serialize_arg(v)}" for k, v in sorted(kwargs.items()))
    return ":".join(parts)


def _serialize_arg(arg: Any) -> str:
    """Serialize a single argument into a stable string representation."""
    if isinstance(arg, Path):
        resolved = arg.resolve()
        content_hash = _file_hash(resolved) if resolved.is_file() else "missing"
        return f"path:{resolved}:{content_hash}"
    return repr(arg)


def _file_hash(path: Path) -> str:
    """Return a hex SHA-256 digest of a file's contents."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def cached(func: Any) -> Any:
    """Decorator that caches a function's return value on disk.

    The cache key is derived from the function name and its arguments.
    Path arguments are content-hashed so that stale results are
    automatically invalidated when the file changes.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Skip `self` for bound methods — __qualname__ already encodes the class.
        cache_args = args[1:] if args and hasattr(args[0], func.__name__) else args
        key = _make_key(func.__qualname__, cache_args, kwargs)
        cache = _get_cache()
        if key in cache:
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper
