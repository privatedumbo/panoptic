# Panoptic

PDF entity extraction, resolution, and knowledge graph linking pipeline.

Panoptic parses PDF documents, extracts named entities (people, organisations, locations) using NER, resolves them to canonical forms via an LLM, and links them to [Wikidata](https://www.wikidata.org/) — enabling roll-up and roll-down across the Wikidata type hierarchy.

## Table of contents

- [How it works](#how-it-works)
- [Quick start](#quick-start)
  - [Try it out](#try-it-out)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [LLM providers](#llm-providers)
- [Development](#development)
- [License](#license)

## How it works

```
PDF  →  Text extraction (Docling)
     →  Named Entity Recognition (spaCy / semantica)
     →  Entity Resolution (LLM via litellm)
     →  Wikidata Linking (wbsearchentities + SPARQL)
     →  Canonical entities with QIDs, types, and grouped mentions
```

## Quick start

This project uses [UV](https://docs.astral.sh/) as its package manager.

```bash
# Install dependencies
uv run poe sync

# Install pre-commit hooks
uv run poe install-hooks
```

### Try it out

Download a sample PDF into the `data/` folder and run the pipeline:

```bash
# Download a paper (any PDF works)
curl -L -o data/sample.pdf "https://arxiv.org/pdf/2501.00001v1"

# Run the pipeline
uv run panoptic/main.py data/sample.pdf
```

### Usage

```bash
# Or as a module
python -m panoptic.main path/to/document.pdf
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
| `PANOPTIC_WIKIDATA_ENABLED` | `True` | Enable Wikidata entity linking |
| `PANOPTIC_WIKIDATA_LANGUAGE` | `en` | Language for Wikidata search and labels |

#### LLM providers

Panoptic uses [litellm](https://docs.litellm.ai/docs/providers) for LLM calls, so any provider it supports works out of the box. Set the model via `PANOPTIC_LLM_MODEL` and the provider's API key via the corresponding environment variable:

| Provider | Model example | API key variable |
|---|---|---|
| OpenAI | `openai/gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| Groq | `groq/llama-3.1-70b-versatile` | `GROQ_API_KEY` |
| Google Gemini | `gemini/gemini-2.0-flash` | `GEMINI_API_KEY` |

```bash
# Example: switch to Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
export PANOPTIC_LLM_MODEL="anthropic/claude-sonnet-4-20250514"

uv run panoptic/main.py data/sample.pdf
```

See the [litellm provider docs](https://docs.litellm.ai/docs/providers) for the full list of supported providers and their required environment variables.

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
