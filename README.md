# Pathfinder 1e Advisor — MCP Server

An MCP server that turns Claude into an expert Pathfinder 1st Edition advisor. Backed by a local SQLite database of comprehensive game data and a curated library of 79 community optimization guides covering 37 of 38 PF1e classes.

## What It Does

- **Rules lookup** — Search spells, feats, classes, archetypes, items, and more from a local database of ~13,000 entries with full-text search
- **Build advice** — Search 79 community optimization guides for feat/spell ratings, archetype analysis, and build recommendations
- **Character sheets** — Standardized multi-file character format with full stat breakdowns and live combat state tracking
- **Combat assistance** — Advisor behavior guidelines for buff stacking, Discord dice commands, and state management
- **Prerequisite checking** — Verify feat prerequisites and archetype compatibility against character stats
- **Read-through cache** — Missing data is fetched from aonprd.com/d20pfsrd.com and cached locally for future use
- **Reference docs** — Character format specs, advisor behavior rules, and guide conventions served on demand via `get_reference()`

## Setup

```bash
# Clone the repo
git clone https://github.com/g-georgiev/pathfinder-mcp
cd pathfinder-mcp

# Option A: One-command setup + add to your project
./setup.sh /path/to/your/project

# Option B: Manual setup
python3 -m venv mcp-server/.venv && mcp-server/.venv/bin/pip install mcp
claude mcp add --scope project --transport stdio pathfinder-data -- \
  $(pwd)/mcp-server/.venv/bin/python3 $(pwd)/mcp-server/server.py
```

The SQLite database ships with the repo — no build step needed.

Then add the bootstrap to your project's `CLAUDE.md` (see `config-templates/CLAUDE.md`).

## Architecture

```
pathfinder/agent/
├── mcp-server/
│   └── server.py            # MCP server — 21 tools
├── db/
│   ├── build.py             # Rebuilds DB from JSON (see data/db-restore branch)
│   └── pathfinder.db        # SQLite database (~13MB, checked in)
├── data/
│   ├── characters/
│   │   ├── FORMAT.md        # Character sheet + state format specification
│   │   └── samples/         # Pre-built sample characters (normal/ and gestalt/)
│   └── guides/              # 79 community optimization guides (14MB)
│       └── INDEX.md         # Guide index by class
├── docs/                    # Reference docs served by get_reference()
│   ├── advisor.md           # Advisor behavior, combat math, Discord dice syntax
│   ├── mcp-tools.md         # MCP tool reference and stub enrichment protocol
│   ├── characters.md        # Character sheet conventions
│   ├── campaign.md          # Campaign data conventions
│   └── guides.md            # Guide usage instructions
├── scripts/
│   ├── src/                 # Data pipeline (PSRD + aonprd extraction & merge)
│   └── data/output/         # Generated JSON (gitignored; see data/db-restore branch)
└── config-templates/
    ├── mcp.json             # Starter .mcp.json for consuming projects
    └── CLAUDE.md            # Starter CLAUDE.md bootstrap
```

## Sample Characters

Pre-built characters showcasing the full character sheet format and MCP-driven build process. See [data/characters/samples/](data/characters/samples/) for the full list, organized into [normal/](data/characters/samples/normal/) (single-class) and [gestalt/](data/characters/samples/gestalt/) builds.

| Character | Classes | Level | Type | Concept |
|-----------|---------|-------|------|---------|
| [The McGyver](data/characters/samples/normal/the-mcgyver/sheet.md) | Wizard (Spell Sage) 10 | 10 | Normal | Cross-list casting generalist — casts cleric, druid, and bard spells via Spell Study |
| [The Shwarma Master](data/characters/samples/gestalt/the-shwarma-master/sheet.md) | Magus (Kensai) // Wizard (Foresight Divination) 16 | 16 | Gestalt | Gold-standard gestalt action economy — Spell Combat + Broad Study delivers Wizard touch spells through a scimitar (*Aisha*), paired with passive Kensai INT bonuses to AC, initiative, crits, and AoOs. Also a working Qadiran cook |

Each sample character includes: `sheet.md` (full stat breakdown), `spells.md` (spell descriptions), `features.md` (class features), `feats.md` (feat reference), `backstory.md` (flavor), and `images/` (portraits + generation prompt).

## MCP Tools (21 tools)

### Game Data (13K entries, FTS5 search)
| Tool | Purpose |
|------|---------|
| `search_spells` | Search by name, school, class, max level |
| `search_feats` | Search by name, type, prerequisite |
| `search_classes` | Search by name, type (core/base/hybrid/prestige) |
| `search_archetypes` | Search by name, base class |
| `search_items` | Search magic items by name, category, slot |
| `search_equipment` | Search mundane equipment by name, category |
| `search_races` | Search by name, size |
| `search_class_options` | Search domains, bloodlines, mysteries, patrons |
| `get_detail` | Full data for any entry by table + ID |
| `get_skills` | All 26 PF1e skills |
| `check_feat_prerequisites` | Verify feat eligibility against character stats |
| `check_archetype_compatibility` | Check if archetypes conflict |
| `cache_entry` | Store web-fetched data for future queries |
| `db_stats` | Row counts per table |

### Sample Characters & Portraits
| Tool | Purpose |
|------|---------|
| `list_sample_characters` | List available sample builds, optionally filtered by type (normal/gestalt) |
| `get_sample_character` | Read a sample character's sheet, spells, feats, features, or backstory |
| `compare_with_sample` | Compare a user's build against a sample for optimization insights |
| `generate_portrait_prompt` | Generate an image-gen prompt from character data, saved to `images/prompt.md` |

### Guides (79 guides, 37/38 classes)
| Tool | Purpose |
|------|---------|
| `search_guides` | Grep across all guides for build advice |
| `get_guide_index` | Full guide listing by class |

### Reference
| Tool | Purpose |
|------|---------|
| `get_reference` | Serve docs on demand: format, advisor, mcp, characters, campaign, guides |

## Guide Sources & Attribution

The `data/guides/` directory contains optimization guides written by the Pathfinder community. These guides are publicly shared resources created to help players build better characters. They are included here in restructured form as a knowledge base, with full attribution to their original authors.

**If you are an author listed below and would like your content removed from this repository, please open an issue or contact the maintainer directly. Your content will be removed promptly.**

### 79 guides, 349 files, 14MB — [Full Index](data/guides/INDEX.md)

| Author | Guides | Classes Covered |
|--------|--------|-----------------|
| Iluzry | 13 | Alchemist, Arcanist, Barbarian, Bard, Cleric, Druid (2), Paladin, Psychic, Shaman, Slayer, Sorcerer (2) |
| Allerseelen | 7 | Inquisitor, Investigator, Kineticist, Mesmerist, Occultist, Oracle, Vigilante |
| N. Jolly | 6 | Alchemist, Barbarian, Gunslinger, Kineticist, Summoner, Warpriest |
| Tark | 2 | Cleric, Summoner |
| Archmage Variel | 1 | Shifter |
| Bodhi | 1 | Inquisitor |
| BrotherPatrick | 1 | Magic Items (general) |
| Cartmanbeck | 1 | Fighter (Iron Caster) |
| CockroachTeaParty | 1 | Medium |
| Dawar | 1 | Arcanist |
| Deadeye | 1 | Paladin (Archery) |
| Forger | 1 | Magus |
| JAM | 1 | Monk |
| kjb200 | 1 | Rogue |
| Kurald Galain | 1 | Magus |
| Lokotor | 1 | Gunslinger |
| Marshmallow | 1 | Fighter |
| Owl | 1 | Witch |
| platinumCheesecake | 1 | Cleric/Oracle/Warpriest Spells |
| Professor Q | 1 | Wizard |
| Prometeus | 1 | Druid |
| Rogue Eidolon | 1 | Rogue |
| Significantotter | 1 | Arcane Trickster |
| Treantmonk | 1 | Wizard |
| Trinam | 1 | Barbarian |
| Community | 1 | Gestalt |
| Unknown | 29 | Various (see [INDEX.md](data/guides/INDEX.md)) |

## Game Data Sources

The SQLite database is built from two primary sources:

- **PSRD** (Pathfinder SRD) — Open Game License content extracted from the official SRD databases
- **Archives of Nethys (aonprd.com)** — Spell, feat, and archetype indexes scraped for names, URLs, and brief descriptions

The source JSON files from the data pipeline are preserved on the `data/db-restore` branch for rebuilding the DB if data issues are found. The DB also accumulates web-fetched entries via the `cache_entry` MCP tool (prefixed `web-`).

All Pathfinder game mechanics content is published under the **Open Game License v1.0a** by Paizo Inc.

## License

The source code (Python scripts, MCP server, build tools) is licensed under the **Apache License 2.0** — see [LICENSE](LICENSE).

Guide content in `data/guides/` is the intellectual property of the respective authors listed above, included with attribution for non-commercial community use. It is **not** covered by the Apache license.

Pathfinder is a registered trademark of Paizo Inc. Game mechanics content is used under the Open Game License v1.0a.
