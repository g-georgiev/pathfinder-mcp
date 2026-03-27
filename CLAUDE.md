# Pathfinder 1e Advisor — MCP Server

## What This Is

An MCP server providing Pathfinder 1st Edition game data, optimization guides, and reference documentation. Not a plugin — just add the server to any project's `.mcp.json`.

## Architecture

```
pathfinder/agent/
├── mcp-server/
│   └── server.py               # MCP server (17 tools)
├── db/
│   ├── build.py                # Builds SQLite DB from JSON pipeline output
│   └── pathfinder.db           # Built database (gitignored, ~13MB)
├── data/
│   ├── characters/
│   │   └── FORMAT.md           # Character sheet + state format specification
│   └── guides/                 # 79 community optimization guides
│       └── INDEX.md            # Guide index by class
├── docs/                       # Reference docs served by get_reference()
├── scripts/
│   ├── src/                    # Python data pipeline (PSRD + aonprd)
│   └── data/output/            # Generated JSON (source of truth for DB)
└── examples/                   # Example configs for consuming projects
```

## Setup

```bash
python3 db/build.py
cd mcp-server && python3 -m venv .venv && .venv/bin/pip install mcp
```

## Conventions

- Python scripts use **stdlib only** (plus `requests` for HTTP). No pip for the pipeline.
- MCP server uses the `mcp` package (FastMCP).
- Character and guide data are markdown files — no JSON/YAML serialization layers.
- SQLite DB is gitignored and rebuilt from JSON via `python3 db/build.py`.
- ID slugs use `source+name` or `source+class+name` patterns with `-` separators.
- Use `INSERT OR IGNORE` for seeding (merged data has ID collisions).
- Reference docs in `docs/` are served via the `get_reference()` MCP tool to consuming projects.
