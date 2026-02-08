# Panoptic

PDF entity extraction and resolution pipeline.

Panoptic parses PDF documents, extracts named entities (people, organisations, locations) using NER, and resolves them to canonical forms via an LLM — grouping every mention that refers to the same real-world entity.

## How it works

```
PDF  →  Text extraction (Docling)
     →  Named Entity Recognition (spaCy / semantica)
     →  Entity Resolution (LLM via litellm)
     →  Canonical entities with grouped mentions
```

## Quick start

This project uses [UV](https://docs.astral.sh/) as its package manager.

```bash
# Install dependencies
uv run poe sync

# Install pre-commit hooks
uv run poe install-hooks
```

### Usage

```bash
# Via CLI
panoptic path/to/document.pdf

# Or as a module
python -m panoptic.main path/to/document.pdf
python -m panoptic.main data/karma_flows.pdf
```

### Configuration

All settings can be overridden via environment variables with the `PANOPTIC_` prefix:

| Variable | Default | Description |
|---|---|---|
| `PANOPTIC_LLM_MODEL` | `openai/gpt-4o-mini` | LLM model (any litellm-compatible string) |
| `PANOPTIC_NER_MODEL` | `en_core_web_trf` | spaCy NER model |
| `PANOPTIC_NER_METHODS` | `ml,pattern` | NER extraction methods |
| `PANOPTIC_NER_ENTITY_TYPES` | `PERSON,ORG,GPE` | Entity types to extract |
| `PANOPTIC_NER_MIN_CONFIDENCE` | `0.6` | Minimum NER confidence threshold |
| `PANOPTIC_CACHE_DIR` | `~/.cache/panoptic` | Disk cache directory |

## Development

```bash
uv run poe format   # Format code (ruff)
uv run poe lint     # Lint and auto-fix (ruff)
uv run poe check    # Type check (mypy)
uv run poe test     # Run tests (pytest)

uv run poe flc      # Format → Lint → Check
uv run poe flct     # Format → Lint → Check → Test
```

## License

MIT
