from panoptic.extraction import EntityExtractor
from panoptic.parse import DocumentParser
from panoptic.resolution import EntityResolver
from panoptic.settings import get_settings
from panoptic.utils import path_from_args
from panoptic.wikidata import WikidataLinker


def main() -> None:
    """Run the panoptic entity extraction and resolution pipeline."""
    path = path_from_args()

    settings = get_settings()
    parser = DocumentParser()
    extractor = EntityExtractor(settings)
    resolver = EntityResolver(settings)
    linker = WikidataLinker(settings)

    document = parser.parse(path)
    mentions = extractor.extract_entities(document)
    result = resolver.resolve_entities(document, mentions)

    if settings.wikidata_enabled:
        result = linker.link(result, document.text)

    print(result.display())


if __name__ == "__main__":
    main()
