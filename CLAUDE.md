# Pathfinder 1e Advisor — MCP Server

## What This Is

An MCP server providing Pathfinder 1st Edition game data, optimization guides, character management, combat resolution, and campaign tracking. Standalone MCP server — add to any project's `.mcp.json`.

## Architecture

```
pathfinder/agent/
├── mcp-server/
│   ├── server.py               # MCP server entry point (56 tools)
│   ├── game_state.py           # Game state DB: schema DDL, get_game_db()
│   ├── tools/                  # Game state tool modules (7 files)
│   └── compute/                # PF1e derived stat engine (7 files)
├── prep-agent/
│   ├── agent.py                # Local LLM agent for character creation
│   ├── llm_client.py           # OpenAI-compatible HTTP client
│   └── prompts/                # System prompts (chargen.md, npc_gen.md)
├── db/
│   ├── pathfinder.db           # Rules database (~13MB, checked into git)
│   ├── game_state.db           # Game state database (gitignored, auto-created)
│   └── build.py                # Rebuilds rules DB from JSON (use with data/db-restore branch)
├── data/
│   ├── characters/
│   │   ├── FORMAT.md           # Character sheet + state format specification
│   │   └── samples/            # Pre-built sample characters (served by MCP tools)
│   └── guides/                 # 79 community optimization guides
│       └── INDEX.md            # Guide index by class
├── docs/                       # Reference docs served by get_reference()
├── scripts/
│   ├── src/                    # Python data pipeline (PSRD + aonprd)
│   └── data/output/            # Generated JSON (gitignored; see data/db-restore branch)
└── config-templates/           # Starter configs for consuming projects
```

## Setup

```bash
cd mcp-server && python3 -m venv .venv && .venv/bin/pip install mcp
```

The rules database ships with the repo. Game state database is auto-created on first access.

## Conventions

- Python scripts use **stdlib only** (plus `requests` for HTTP). No pip for the pipeline.
- MCP server uses the `mcp` package (FastMCP).
- Original 21 rules tools use `@mcp.tool()` in `server.py`. New 35 game state tools are plain functions in `tools/` modules, registered via `mcp.add_tool()` in `tools/__init__.py`.
- Two SQLite databases, one MCP process:
  - `pathfinder.db` — rules reference (static, git-tracked). Connection via `get_db()` in `server.py`.
  - `game_state.db` — game state (dynamic, gitignored). Connection via `get_game_db()` in `game_state.py`. Auto-creates tables on first access.
- Character data is JSON blobs in SQLite (`data` column). Derived stats are pre-computed and stored in a separate `computed` JSON column.
- `render_character_md` produces FORMAT.md-spec Markdown from JSON. `import_character_md` parses Markdown back to JSON.
- Tool functions are plain Python — importable directly by the prep agent and game server without MCP protocol.
- Error handling: tools return `{"error": "message"}` dicts, never raise exceptions.
- ID generation: `uuid.uuid4().hex[:12]` for sessions/players, `slugified-name-uuid4().hex[:8]` for characters.
- Source JSON files are on the `data/db-restore` branch for pipeline debugging.
- Reference docs in `docs/` are served via the `get_reference()` MCP tool.

## Testing

```bash
cd mcp-server && .venv/bin/python -m pytest tests/ -v
```

104 tests across 10 test files. Fixtures in `tests/conftest.py` provide a fresh temp `game_state.db` per test and read-only access to the real `pathfinder.db`.

## Part of the AI DM Project

This MCP is one of three repos in the Pathfinder AI DM collaboration:
1. **pathfinder-mcp** (this repo) — rules reference + game state tools + prep agent
2. **pathfinder-dm-server** — WebSocket game server with LLM agent loop (see `../dm-server/PRD.md`)
3. **dungeon-ai** — Electron thin client (Stefan)
