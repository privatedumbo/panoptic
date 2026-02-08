from pathlib import Path

from semantica.parse import DoclingParser

from panoptic.cache import cached
from panoptic.models import Document


class DocumentParser:
    """Extract plain text from a document via Docling."""

    def __init__(self) -> None:
        self._parser = DoclingParser(enable_ocr=True)

    @cached
    def parse(self, path: Path) -> Document:
        """Parse *path* and return a typed Document."""
        result = self._parser.parse(path)
        return Document(text=result["full_text"], source=path)
