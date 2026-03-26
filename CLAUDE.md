# Pathfinder 1e Advisor — Claude Code Plugin

## What This Is

A Claude Code plugin that turns Claude into an expert Pathfinder 1st Edition advisor. Instead of a web UI, the interface is conversational — backed by a local SQLite database of comprehensive game data and an MCP server for precision queries.

## Architecture

```
pathfinder/agent/
├── plugin.json                 # Claude Code plugin manifest
├── .mcp.json                   # MCP server configuration
├── .claude/rules/              # Advisor behavior, MCP tools, character conventions
├── db/
│   ├── build.py                # Builds SQLite DB from JSON pipeline output
│   └── pathfinder.db           # Built database (gitignored, ~13MB)
├── mcp-server/
│   └── server.py               # MCP server — exposes query tools to Claude
├── data/
│   ├── characters/             # Character sheet directories (one per character)
│   │   └── FORMAT.md           # Character sheet + state format specification
│   └── guides/                 # Normalized optimization guides (markdown)
├── agents/
│   └── character-builder.md    # File generation agent (reads pre-fetched data, writes sheets)
├── skills/
│   └── create-character/       # /create-character — MCP lookups + spawns character-builder
├── scripts/
│   ├── src/                    # Python data pipeline (PSRD + aonprd)
│   └── data/output/            # Generated JSON (source of truth for DB)
```

## Setup

```bash
# Build the SQLite database from JSON data
python3 db/build.py

# Install MCP server dependency
pip install mcp
```

## Data Pipeline

Python scripts in `scripts/src/` extract, scrape, and merge Pathfinder data:
- **Source**: PSRD SQLite databases + aonprd.com scraping
- **Output**: JSON files in `scripts/data/output/`
- **DB Build**: `db/build.py` loads JSON into SQLite with FTS5 indexes

Pipeline runs from `/scripts/` via `python3 src/run.py`.

### Data Inventory

| Table | Source File | Count | Notes |
|---|---|---|---|
| skills | skills.json | 26 | All PF1e skills |
| races | races.json | 44 | With 244 alternate racial traits |
| classes | classes.json | 55 | Including 18 prestige with requirements |
| archetypes | merged_archetypes.json | ~1,540 | With replaced_features for compatibility |
| spells | merged_spells.json | ~3,059 | PSRD + aonprd merged |
| feats | merged_feats.json | ~3,625 | With parsed prerequisites |
| items | items.json | 3,715 | Magic items with slots, aura, construction |
| equipment | equipment.json | 1,231 | Weapons, armor, gear with stats |
| class_options | class_options.json | 160 | Domains, bloodlines, mysteries, patrons |

## Guides

Optimization guides normalized into markdown in `data/guides/`. Consistent frontmatter with title, author, source URL, topics, and class tags. Searchable with grep.

```yaml
---
title: Oracle Melee Build Guide
author: Treantmonk
source: <original URL>
topics: [oracle, melee, revelations, battle oracle]
classes: [oracle]
---
```

## Conventions

- Python scripts use **stdlib only** (plus `requests` for HTTP). No pip for the pipeline.
- MCP server uses the `mcp` package (FastMCP).
- Character and guide data are markdown files — no JSON/YAML serialization layers.
- SQLite DB is gitignored and rebuilt from JSON via `python3 db/build.py`.
- ID slugs use `source+name` or `source+class+name` patterns with `-` separators.
- Use `INSERT OR IGNORE` for seeding (merged data has ID collisions).
- Subagents cannot access plugin MCP tools — use the pre-fetch pattern (skill does lookups, writes to temp file, agent reads it).
