# Pathfinder 1e Advisor — MCP Server

An MCP server that turns any AI agent into an expert Pathfinder 1st Edition advisor with comprehensive rules lookup, character management, combat resolution, and campaign tracking. Backed by a local SQLite database of ~13,000 game entries, 79 community optimization guides, and a complete game state engine.

## What It Does

**Rules Reference (21 tools)**
- Search spells, feats, classes, archetypes, items, equipment, races, class options with full-text search
- Verify feat prerequisites and archetype compatibility against character stats
- Search 79 optimization guides for feat/spell ratings and build recommendations
- Read-through cache: missing data is fetched from aonprd.com/d20pfsrd.com and cached locally

**Game State (35 tools)**
- Session management with save/load snapshots
- Character persistence with automatic derived stat computation (HP, BAB, saves, AC, attacks, skills, spell slots, CMB/CMD)
- Live state tracking: HP, conditions, inventory, spell slots, level-up
- NPC management (full stat blocks or sparse stat-block-only entries)
- Combat: initiative, attack/save/skill resolution, turn tracking, condition expiry
- Campaign memory: event log with FTS5 search, quest tracking, foreshadowing threads

**Prep Agent**
- Standalone local LLM agent for character creation (Gemma 4 26B A4B or any OpenAI-compatible endpoint)
- Imports MCP tools as Python functions directly — no protocol overhead
- Iteratively researches and builds PF1e characters through tool calls

## Part of the AI DM Project

This MCP is one of three repos in the Pathfinder AI DM collaboration:

| Repo | Role |
|---|---|
| **pathfinder-mcp** (this repo) | PF1e rules reference + stateful game tools + prep agent |
| [pathfinder-dm-server](https://github.com/g-georgiev/pathfinder-dm-server) | WebSocket game server with LLM agent loop |
| [dungeon-ai](https://github.com/Lewandowskista/DungeonAI) | Electron thin client |

This MCP runs standalone — no game server required. Add it to any project's `.mcp.json` for PF1e rules lookup, character management, and game state tracking from any AI agent.

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

The SQLite database ships with the repo — no build step needed. Game state database (`game_state.db`) is auto-created on first use.

## Architecture

```
pathfinder-mcp/
├── mcp-server/
│   ├── server.py               # MCP server entry point (56 tools)
│   ├── game_state.py           # Game state DB schema + connection management
│   ├── tools/                  # Game state tool modules
│   │   ├── session.py          #   Session lifecycle (6 tools)
│   │   ├── character.py        #   Character persistence (3 tools)
│   │   ├── character_updates.py#   HP, conditions, inventory, spells, level-up (5 tools)
│   │   ├── npc.py              #   NPC management (4 tools)
│   │   ├── combat.py           #   Combat resolution (7 tools)
│   │   ├── campaign.py         #   Campaign memory (8 tools)
│   │   └── rendering.py        #   MD export/import (2 tools)
│   ├── compute/                # PF1e derived stat engine
│   │   ├── derived.py          #   Orchestrator
│   │   ├── progression.py      #   Class data lookup from rules DB
│   │   ├── hp.py               #   Hit point computation
│   │   ├── saves.py            #   Saving throw computation
│   │   ├── combat_stats.py     #   AC, BAB, CMB/CMD, initiative, attack lines
│   │   ├── skills.py           #   Skill total computation
│   │   └── spells.py           #   Spell slot computation (+ fallback tables)
│   └── tests/                  # 104 tests (pytest)
├── prep-agent/
│   ├── agent.py                # Local LLM agent loop for character creation
│   ├── llm_client.py           # OpenAI-compatible HTTP client
│   └── prompts/                # System prompts (chargen.md, npc_gen.md)
├── db/
│   ├── pathfinder.db           # Rules database (~13MB, git-tracked)
│   ├── game_state.db           # Game state database (gitignored, auto-created)
│   └── build.py                # Rules DB builder (use with data/db-restore branch)
├── data/
│   ├── characters/
│   │   ├── FORMAT.md           # Character sheet format specification
│   │   └── samples/            # Pre-built sample characters
│   └── guides/                 # 79 community optimization guides (14MB)
│       └── INDEX.md            # Guide index by class
├── docs/                       # Runtime reference docs (served by get_reference())
├── scripts/                    # Data pipeline (PSRD + aonprd extraction)
└── config-templates/           # Starter configs for consuming projects
```

## MCP Tools (56 tools)

### Rules Reference (13K entries, FTS5 search)

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
| `list_sample_characters` | List available sample builds (normal/gestalt) |
| `get_sample_character` | Read a sample character's sheet, spells, feats, features, or backstory |
| `compare_with_sample` | Compare a user's build against a sample for optimization insights |
| `generate_portrait_prompt` | Generate an image-gen prompt from character data |

### Guides (79 guides, 37/38 classes)

| Tool | Purpose |
|------|---------|
| `search_guides` | Grep across all guides for build advice |
| `get_guide_index` | Full guide listing by class |

### Reference

| Tool | Purpose |
|------|---------|
| `get_reference` | Serve docs on demand: format, advisor, mcp, characters, campaign, guides |

### Session Management

| Tool | Purpose |
|------|---------|
| `create_session` | Create a new game session (name, tone, setting, DM notes) |
| `get_session` | Get session metadata + player list |
| `list_sessions` | List all sessions |
| `join_session` | Add a player to a session |
| `save_session` | Snapshot all session state for later restore |
| `load_session` | Restore session from most recent snapshot |

### Character Persistence

| Tool | Purpose |
|------|---------|
| `persist_character` | Store a character, compute derived stats (HP, BAB, saves, AC, attacks, skills, spell slots) |
| `get_character` | Full character data + computed stats + active conditions |
| `list_characters` | Summary of all characters in a session |

### Character State Updates

| Tool | Purpose |
|------|---------|
| `update_character_hp` | Apply damage/healing, track unconscious/dying/dead status |
| `update_character_conditions` | Add/remove conditions with duration tracking |
| `update_character_inventory` | Add/remove items, adjust gold |
| `update_character_spells` | Track spell slot usage and restoration |
| `apply_level_up` | Apply level-up choices, recompute all derived stats |

### NPC Management

| Tool | Purpose |
|------|---------|
| `persist_npc` | Store NPC (sparse stat block or full class build) |
| `get_npc` | Full NPC data |
| `list_npcs` | List NPCs with role/location/status filters |
| `update_npc` | Update NPC fields (disposition, HP, location, notes) |

### Combat

| Tool | Purpose |
|------|---------|
| `start_combat` | Initialize encounter with initiative ordering |
| `get_combat_state` | Current turn order, HP, conditions for all combatants |
| `resolve_attack` | Roll + AB vs AC, apply damage on hit |
| `resolve_save` | Roll + save bonus vs DC |
| `resolve_skill_check` | Roll + skill total vs DC |
| `advance_turn` | Next combatant, decrement condition durations |
| `end_combat` | End encounter, distribute XP/loot |

### Campaign Memory

| Tool | Purpose |
|------|---------|
| `log_event` | Record a narrative/combat/discovery/dialogue/decision event |
| `recall_events` | Search events by keyword (FTS5), type, participant, significance |
| `add_quest` | Track a new quest |
| `update_quest` | Update quest status/notes |
| `list_quests` | List quests with status filter |
| `add_foreshadow` | Plant a narrative thread with intended payoff |
| `get_foreshadow_threads` | List unresolved or resolved threads |
| `resolve_foreshadow` | Mark a thread as resolved |

### Rendering

| Tool | Purpose |
|------|---------|
| `render_character_md` | Export character as FORMAT.md-spec Markdown |
| `import_character_md` | Import a Markdown character sheet into the database |

## Prep Agent

The prep agent uses a local LLM (Gemma 4 26B A4B or similar) to iteratively build PF1e characters by calling MCP tool functions directly as Python imports.

```bash
# Start the LLM server (requires HIP_VISIBLE_DEVICES=0 on systems with AMD iGPU)
HIP_VISIBLE_DEVICES=0 ~/workspace/models/serve-model.sh gemma-4-26b-a4b-it -c 16384

# Build a character
mcp-server/.venv/bin/python prep-agent/agent.py \
  "human fighter level 1, melee build with longsword and shield"

# Build and persist to a game session
mcp-server/.venv/bin/python prep-agent/agent.py \
  --persist --session-id abc123 \
  "dwarven stonelord paladin, level 5"
```

See [prep-agent/README.md](prep-agent/README.md) for full usage.

## Sample Characters

| Character | Classes | Level | Type | Concept |
|-----------|---------|-------|------|---------|
| [The McGyver](data/characters/samples/normal/the-mcgyver/sheet.md) | Wizard (Spell Sage) 10 | 10 | Normal | Cross-list casting generalist |
| [The Shwarma Master](data/characters/samples/gestalt/the-shwarma-master/sheet.md) | Magus (Kensai) // Wizard (Foresight Divination) 16 | 16 | Gestalt | Action economy powerhouse |

## Tests

```bash
cd mcp-server && .venv/bin/pip install pytest && .venv/bin/python -m pytest tests/ -v
```

104 tests covering compute engine, session lifecycle, character persistence, combat resolution, campaign memory, NPC management, and MD rendering.

## Databases

| Database | Purpose | Lifecycle |
|----------|---------|-----------|
| `pathfinder.db` | Rules reference (~13K entries, 9 tables, FTS5) | Static, git-tracked. Rebuild with `python3 db/build.py` |
| `game_state.db` | Game sessions, characters, combat, campaign memory | Dynamic, gitignored. Auto-created on first use |

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
| *29 more authors* | 51 | Various (see [INDEX.md](data/guides/INDEX.md)) |

## Game Data Sources

- **PSRD** (Pathfinder SRD) — Open Game License content from the official SRD databases
- **Archives of Nethys (aonprd.com)** — Spell, feat, and archetype indexes

Source JSON files are on the `data/db-restore` branch. All Pathfinder game mechanics content is published under the **Open Game License v1.0a** by Paizo Inc.

## License

Source code is licensed under **Apache License 2.0**. Guide content is the intellectual property of the respective authors, included with attribution for non-commercial community use. Pathfinder is a registered trademark of Paizo Inc.
