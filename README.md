# Panoptic

PDF entity extraction and resolution pipeline.

Panoptic parses PDF documents, extracts named entities (people, organisations, locations) using NER, and resolves them to canonical forms via an LLM — grouping every mention that refers to the same real-world entity.

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

### Try it out

Download a sample PDF into the `data/` folder and run the pipeline:

```bash
# Download the paper
curl -L -o data/ssrn-5317150.pdf \
  "https://papers.ssrn.com/sol3/Delivery.cfm/5317150.pdf?abstractid=5317150&mirid=1"

# Run the pipeline
uv run panoptic/main.py data/ssrn-5317150.pdf
```

### Usage

```bash
# Via CLI
panoptic path/to/document.pdf

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

uv run panoptic/main.py data/ssrn-5317150.pdf
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
