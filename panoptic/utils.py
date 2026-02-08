"""CLI argument helpers."""

import sys
from pathlib import Path

EXPECTED_ARGUMENTS = 2


def ensure_path_exists(path: Path) -> Path:
    """Validate that *path* exists and return it.

    Raises:
        FileNotFoundError: If the path does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def path_from_args() -> Path:
    """Extract and validate the document path from CLI arguments.

    Raises:
        SystemExit: If the argument count is wrong.
        FileNotFoundError: If the resolved path does not exist.
    """
    if len(sys.argv) != EXPECTED_ARGUMENTS:
        error_message = "Usage: python -m panoptic.main <path-to-pdf>"
        raise ValueError(error_message)

    return ensure_path_exists(Path(sys.argv[1]))
