# Pathfinder 1e Advisor — Claude Code Plugin

## What This Is

A Claude Code plugin that turns Claude into an expert Pathfinder 1st Edition advisor. Instead of a web UI, the interface is conversational — backed by a local SQLite database of comprehensive game data and an MCP server for precision queries.

## Architecture

```
pathfinder/
├── plugin.json                 # Claude Code plugin manifest
├── db/
│   ├── build.py                # Builds SQLite DB from JSON pipeline output
│   └── pathfinder.db           # Built database (gitignored, ~30MB)
├── mcp-server/
│   └── server.py               # MCP server — exposes query tools to Claude
├── data/
│   ├── characters/             # Character sheet directories (one per character)
│   │   └── FORMAT.md           # Character sheet format specification
│   └── guides/                 # Normalized optimization guides (markdown)
├── agents/
│   └── character-builder.md    # Autonomous agent: builds character sheets from raw input
├── skills/
│   └── create-character.md     # /create-character — user-invocable sheet creation
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
| spells | merged_spells.json | ~3,548 | PSRD + aonprd merged |
| feats | merged_feats.json | ~4,971 | With parsed prerequisites |
| items | items.json | 3,715 | Magic items with slots, aura, construction |
| equipment | equipment.json | 1,231 | Weapons, armor, gear with stats |
| class_options | class_options.json | 160 | Domains, bloodlines, mysteries, patrons |

### MCP Tools

The `pathfinder-data` MCP server (`mcp-server/server.py`) exposes tools prefixed `mcp__pathfinder-data__`. The venv at `mcp-server/.venv/` must have `mcp` installed (`pip install mcp`).

#### Search tools
All search tools accept `query` (name text), type-specific filters, `limit` (default 20), and `expand` (bool).
- **`expand=False`** (default): returns indexed columns only (name, type, source, etc.) — use for scanning/listing
- **`expand=True`**: returns the full JSON data blob (descriptions, progression tables, spell lists, etc.) — use when you need details on specific entries

| Tool | Key filters | Notes |
|---|---|---|
| `search_spells` | `school`, `class_name`, `max_level` | `class_name` filters by class in spell_level text |
| `search_feats` | `feat_type`, `prerequisite` | `prerequisite` is text match on prereq string |
| `search_classes` | `class_type` | Types: base, core, hybrid, prestige, unchained |
| `search_archetypes` | `base_class` | |
| `search_items` | `category`, `slot` | Category: wondrous, weapon, armor, ring, rod, staff |
| `search_equipment` | `category`, `subcategory` | Category: weapon, armor, shield, gear |
| `search_races` | `size` | Size: Small, Medium, Large |
| `search_class_options` | `option_type`, `base_class` | Types: domain, subdomain, bloodline, mystery, patron |

#### Detail & utility tools
- `get_detail(table, id)` — full data for one entry by table name + ID slug
- `get_skills()` — all 26 skills (always expanded)
- `check_feat_prerequisites(feat_name, character_bab, character_level, character_feats, character_abilities, character_skills)` — returns `{qualified, met[], unmet[]}`
- `check_archetype_compatibility(base_class, archetype_names[])` — returns `{compatible, conflicts}`
- `db_stats()` — row counts per table

#### Read-through cache
- `cache_entry(table, id, name, data, source="web", **columns)` — insert/replace an entry found via web search

The DB is a **read-through cache**: if a search returns no results, do a web search (aonprd.com, d20pfsrd.com), normalize the data into the same structure, and call `cache_entry` to store it. Future queries will hit the local DB. Use `source="web"` and prefix IDs with `web-` for cached entries.

## Characters

Each character is a **directory** under `data/characters/` containing multiple linked markdown files:

```
data/characters/nettle/
├── sheet.md        # Main reference — stats, breakdowns, spell quick-reference
├── spells.md       # Full spell descriptions (casting time, range, duration, save, full text)
├── features.md     # Class features, curses, revelations, racial traits, bloodline powers
└── feats.md        # Feat descriptions with prerequisites and interactions
```

### Character sheet conventions

- **Traceability**: Every derived number traces to its source (e.g. AC 16 = 10 base + 2 DEX + 4 Mage Armor). Show the math.
- **Spell tables**: Main sheet has one-line summaries (action, range, duration, effect). Full descriptions with tactical notes in `spells.md`.
- **Linked references**: Use `[Spell Name](spells.md#spell-name)` links throughout. Every mention of a spell, feat, or feature should link to its full description.
- **Back-to-sheet links**: Every section in reference files ends with `[← Sheet](sheet.md)` for easy navigation.
- **Planned vs current**: Anything not yet available at current level is marked with `*(planned)*`.
- **Source attribution**: Feats show which level they were taken. Spells show their source (chosen, bloodline bonus, curse bonus, archetype). Skills show what contributes to each bonus.
- **Frontmatter**: `sheet.md` has YAML frontmatter with name, level, classes, race for quick identification.

### Data completeness

Some DB entries have stub descriptions (short summary only, no full benefit text). When writing or updating character sheets:
1. Check DB for full data (`expand=True`)
2. If the description is a stub, web search aonprd.com or d20pfsrd.com
3. Cache the full data back to DB via `cache_entry`
4. Write the complete description to the character's reference file

## Personal Data

Campaign-specific data (characters, guides, house rules) lives in a separate directory/repo. Check for a sibling `personal/` directory or the user's own CLAUDE.md for campaign house rules. Character sheets are stored under the personal data directory, not in this plugin.

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
