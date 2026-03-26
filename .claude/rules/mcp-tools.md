# MCP Tools Reference

The `pathfinder-data` MCP server (`mcp-server/server.py`) exposes tools prefixed `mcp__pathfinder-data__`. The venv at `mcp-server/.venv/` must have `mcp` installed (`pip install mcp`).

## Search Tools

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

## Detail & Utility Tools

- `get_detail(table, id)` — full data for one entry by table name + ID slug
- `get_skills()` — all 26 skills (always expanded)
- `check_feat_prerequisites(feat_name, character_bab, character_level, character_feats, character_abilities, character_skills)` — returns `{qualified, met[], unmet[]}`
- `check_archetype_compatibility(base_class, archetype_names[])` — returns `{compatible, conflicts}`
- `db_stats()` — row counts per table

## Read-Through Cache

- `cache_entry(table, id, name, data, source="web", **columns)` — insert/replace an entry found via web search

The DB is a **read-through cache**: if a search returns no results, do a web search (aonprd.com, d20pfsrd.com), normalize the data into the same structure, and call `cache_entry` to store it. Future queries will hit the local DB. Use `source="web"` and prefix IDs with `web-` for cached entries.

## Stub Records and Lazy Enrichment

Many DB entries have incomplete data (short summary instead of full description, missing school/class levels for spells, missing parsed prerequisites for feats). When you query with `expand=True`, stub records are flagged with `_stub: true`.

**When you encounter `_stub: true` and need the full data:**

1. **Web fetch** the record's `url` field (aonprd.com or d20pfsrd.com)
2. **Extract** the missing fields (full description, school, class/level list, prerequisites, etc.)
3. **Cache** the enriched data via `cache_entry` using the record's existing `id` — this replaces the stub with complete data for all future queries

This is the expected workflow — the DB was bulk-seeded from indexes that only have summaries. Full data gets backfilled on demand as you use it. Don't flag stub records as errors; just enrich them when you need the detail.

**What counts as a stub by table:**
- **spells**: description < 100 chars (most are one-line summaries like "1d6 fire damage per level")
- **feats**: benefit < 50 chars (aonprd index entries have only a brief summary)
- **archetypes, items, equipment, class_options**: description < 50 chars
