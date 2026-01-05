# Copilot Instructions for Refrain

## Project Overview
Refrain is a Python AI code assistant CLI tool that embodies "iterative refinement with restraint" — providing transparent, user-confirmed code modifications through LLM-powered analysis.

**Core Philosophy**: Diff transparency + user confirmation before any code change. Never black-box modifications.

## Architecture (Six-Layer Design)

```
src/refrain/
├── cli/              # Command-line interface layer
│   ├── main.py       # Entry point + subcommand registry
│   └── commands/     # Subcommand modules (model, config, etc.)
├── core/             # Infrastructure layer (config, LLM client)
│   ├── config/       # Model profiles, settings (~/.refrain/config.json)
│   └── llm/          # OpenAI client wrapper (supports multi-model)
├── engine/           # Orchestration layer
│   └── orchestrator/ # ReAct loop for AI decision-making
├── skills/           # Tool layer (Function Calling)
│   ├── base/         # Skill base class
│   ├── registry/     # Centralized skill registration
│   └── toolbox/      # Concrete skill implementations
├── utils/            # Utilities (fs, UI)
└── resources/        # Prompt templates (system.md)
```

## Key Conventions

### 1. CLI Subcommand Pattern
**All subcommands register in `cli/main.py`**:
```python
from .commands import model
app.add_typer(model.app, name="model", help="模型管理")
```

**Subcommand modules** (`cli/commands/*.py`):
- Create a `typer.Typer()` instance (no help text here)
- Define commands with `@app.command()` decorator
- Import and register in `main.py`

**Example**: See `cli/commands/model.py` for reference implementation.

### 2. Folder vs File Decision
- **Use folders** when expecting multi-file modules (e.g., `cli/commands/`)
- **Use `.py` files** when single-file is sufficient (future: convert `core/config/`, `core/llm/` to `.py` when implementing)
- All modules currently have `__init__.py` placeholders with TODO comments

### 3. Configuration Management
- API keys: `.env` file (never commit, use `.env.example` template)
- Model profiles: `~/.refrain/config.json` (user config, separate from codebase)
- System prompts: `src/refrain/resources/system.md`

### 4. Tech Stack Specifics
- **CLI**: Typer (type-safe, auto-generated help)
- **UI**: Rich (syntax highlighting, tables, progress)
- **LLM**: OpenAI SDK (direct, no LangChain in MVP)
- **Config**: Pydantic models + python-dotenv

### 5. Entry Points
```toml
# pyproject.toml
[project.scripts]
rf = "refrain.cli:app"        # Short alias
refrain = "refrain.cli:app"   # Full command
```
Both resolve to `cli/__init__.py` which imports `app` from `main.py`.

## Development Workflows

### Install & Run
```bash
pip install -e .              # Editable install (src layout)
rf --help                     # Test CLI
rf version                    # Check installation
pytest                        # Run tests
```

### Adding a New Subcommand
1. Create `cli/commands/mycommand.py`:
   ```python
   import typer
   app = typer.Typer()
   
   @app.command()
   def my_action():
       pass
   ```
2. Register in `cli/main.py`:
   ```python
   from .commands import mycommand
   app.add_typer(mycommand.app, name="mycommand", help="...")
   ```

### Adding a New Skill (Tool)
1. Define in `skills/toolbox/__init__.py`:
   ```python
   from ..base import Skill
   from pydantic import BaseModel
   
   class MySkillArgs(BaseModel):
       param: str
   
   my_skill = Skill(
       name="my_skill",
       description="...",
       parameters=MySkillArgs,
       func=lambda param: result
   )
   ```
2. Register in `skills/registry/__init__.py`:
   ```python
   skill_registry.register(my_skill)
   ```

## Critical Patterns

### ReAct Loop (Future Implementation)
Located in `engine/orchestrator/`:
- Loop up to 5 iterations
- Check `msg.tool_calls` → execute skills → append results
- Final iteration returns `<reasoning>` and `<code>` XML tags
- Never auto-apply changes — always show diff and confirm

### Model Switching
Managed in `core/config/`:
- Default models: gpt-4o, gpt-3.5, deepseek
- Config stored in `~/.refrain/config.json`
- Switch via `rf model use <name>`
- Client reloads on config change

### UI Rendering
Use Rich components:
- `Console.print()` with markup: `[bold blue]text[/]`
- `Table` for structured data (model lists)
- `Syntax` for code/diff display
- `Panel` for AI reasoning output

### Documentation & Diagrams
**Important**: When creating documentation with diagrams:
- Use Mermaid diagram syntax (```mermaid ... ```) for all visualizations
- Never use ASCII art for diagrams or flowcharts
- Mermaid supports: flowcharts, sequence diagrams, state diagrams, gantt charts, etc.
- This ensures diagrams render properly in GitHub, GitLab, Notion and other platforms
- Example: Use `graph TD` for top-down flowcharts, not ASCII boxes and pipes

## Testing Strategy
- Location: `tests/` (separate from `src/`)
- CLI testing: Use `typer.testing.CliRunner`
- Fixtures: Defined in `conftest.py`
- TODO markers: Tests with implementation dependencies marked clearly

## Project Structure Notes
- **src layout**: Prevents accidental local imports during development
- **z_docs/**: Documentation folder (z_ prefix keeps it at bottom of file lists)
- **Folder structure**: All modules use folders (`cli/commands/`, `core/config/`) for future extensibility, even if currently single-file

## Common Gotchas
- Entry point is `refrain.cli:app`, NOT `refrain.cli.main:app`
- All `__init__.py` files must export properly (use `from .x import y`)
- Rich requires explicit `Console()` instance for styled output
- Typer subcommands need `app.add_typer()`, not simple imports

## Questions for Contributors
When implementing missing modules, consider:
- Should `core/config/` and `core/llm/` collapse to single `.py` files?
- How to handle multi-model API key management securely?
- What's the error handling strategy for LLM API failures?
