# Pathfinder 1e Advisor — MCP Server

## What This Is

An MCP server providing Pathfinder 1st Edition game data, optimization guides, and reference documentation. Not a plugin — just add the server to any project's `.mcp.json`.

## Architecture

```
pathfinder/agent/
├── mcp-server/
│   └── server.py               # MCP server (17 tools)
├── db/
│   ├── build.py                # Rebuilds DB from JSON (use with data/db-restore branch)
│   └── pathfinder.db           # SQLite database (~13MB, checked into git)
├── data/
│   ├── characters/
│   │   └── FORMAT.md           # Character sheet + state format specification
│   └── guides/                 # 79 community optimization guides
│       └── INDEX.md            # Guide index by class
├── docs/                       # Reference docs served by get_reference()
├── scripts/
│   ├── src/                    # Python data pipeline (PSRD + aonprd)
│   └── data/output/            # Generated JSON (gitignored; see data/db-restore branch)
└── examples/                   # Example configs for consuming projects
```

## Setup

```bash
cd mcp-server && python3 -m venv .venv && .venv/bin/pip install mcp
```

The SQLite database ships with the repo — no build step needed.

## Conventions

- Python scripts use **stdlib only** (plus `requests` for HTTP). No pip for the pipeline.
- MCP server uses the `mcp` package (FastMCP).
- Character and guide data are markdown files — no JSON/YAML serialization layers.
- SQLite DB is checked into git as the source of truth. Web-fetched entries (via `cache_entry`) persist across clones.
- Source JSON files are on the `data/db-restore` branch for pipeline debugging. Rebuild with `python3 db/build.py` if needed.
- ID slugs use `source+name` or `source+class+name` patterns with `-` separators. Web-cached entries use `web-` prefix.
- Use `INSERT OR IGNORE` for seeding (merged data has ID collisions).
- Reference docs in `docs/` are served via the `get_reference()` MCP tool to consuming projects.
