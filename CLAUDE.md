# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Refrain is a Python AI code assistant CLI embodying "iterative refinement with restraint" — transparent diff display + user confirmation before any code modification. Core philosophy: Diff transparency + user confirmation before any code change.

## Build & Run Commands

```bash
pip install -e .              # Editable install (src layout)
rf --help                     # Test CLI
rf version                    # Check installation
pytest                        # Run all tests
pytest tests/test_cli.py      # Run specific test file
pytest -v                     # Run with verbose output
```

## Architecture (Six-Layer Design)

```
src/refrain/
├── cli/              # CLI layer - Typer-based command entry points
│   ├── main.py       # App registry + subcommand registration
│   └── commands/     # Subcommand modules (model.py, etc.)
├── core/             # Infrastructure layer
│   ├── config/       # User config (~/.refrain/config.yaml) + schema
│   ├── llm/          # OpenAI-compatible LLM providers
│   │   ├── chat/     # BaseLLM, OpenAIProvider, factory
│   │   └── vector/   # Vector storage (future)
│   └── logger.py     # Loguru-based logging
├── engine/           # Orchestration layer (ReAct loop)
│   └── orchestrator/ # AI decision-making loop
├── skills/           # Tool layer (Function Calling)
│   ├── base/         # Skill base class
│   ├── registry/     # Centralized skill registration
│   └── toolbox/      # Concrete skill implementations
├── utils/            # Utilities (fs, UI with Rich)
└── resources/        # Prompt templates (system.md)
```

## Key Patterns

### CLI Subcommand Registration
All subcommands register in `cli/main.py`:
```python
from .commands import model
app.add_typer(model.app, name="model", help="模型管理")
```

Subcommand modules (`cli/commands/*.py`):
- Create a `typer.Typer()` instance (no help text)
- Define commands with `@app.command()` decorator
- Import and register in `main.py`

### Configuration Management
- **API keys**: `.env` file (never commit)
- **Model profiles**: `~/.refrain/config.yaml` (user config, YAML format)
- **System prompts**: `src/refrain/resources/system.md`
- **Settings**: `core/config/__init__.py` with Pydantic BaseSettings

### LLM Provider Factory
`core/llm/chat/factory.py::get_llm_backend()` provides:
- Profile-based loading: `get_llm_backend(alias="deepseek")`
- Custom instance: `get_llm_backend(provider="openai", api_key="...")`
- Cached singleton via `@lru_cache()`

Provider mapping in `factory.py`:
```python
PROVIDER_MAP = {"openai": OpenAIProvider, "deepseek": OpenAIProvider}
```

### Model Profiles
Defined in `core/config/schema.py::ModelProfile`:
- `name`: alias like "gpt4", "deepseek"
- `provider`: "openai", "deepseek", "anthropic"
- `model`: actual model ID (e.g., "gpt-4o")
- `api_key_env`: env var name for API key
- `base_url`: optional custom API endpoint

### BaseLLM Three-Track Design
`core/llm/chat/base.py` defines three interaction modes:
1. `chat()` - Free-form conversation
2. `structured_chat()` - Pydantic model response (OpenAI parse API)
3. `stream_chat()` - Streaming response with usage stats

## Entry Points

```toml
# pyproject.toml
[project.scripts]
rf = "refrain.cli:app"
refrain = "refrain.cli:app"
```

Both resolve to `cli/__init__.py` importing `app` from `main.py`.

## Tech Stack

- **CLI**: Typer (type-safe, auto-generated help)
- **UI**: Rich (Console, Syntax, Table, Panel)
- **LLM**: OpenAI SDK (async, direct - no LangChain)
- **Config**: Pydantic + Pydantic-Settings + python-dotenv
- **Logging**: Loguru

## Common Gotchas

- Entry point is `refrain.cli:app`, NOT `refrain.cli.main:app`
- All `__init__.py` must export properly (use `from .x import y`)
- Rich requires explicit `Console()` instance for styled output
- Typer subcommands need `app.add_typer()`, not simple imports
- Config stored in YAML format at `~/.refrain/config.yaml`
- API keys read from environment variables (configured in profiles)

## Testing Strategy

- Location: `tests/` (separate from `src/`)
- CLI testing: `typer.testing.CliRunner`
- Fixtures: `conftest.py` (sample_python_file, project_root)
