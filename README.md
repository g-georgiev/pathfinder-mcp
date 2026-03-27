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
# 1. Build the SQLite database from JSON data
python3 db/build.py

# 2. Set up the MCP server venv
cd mcp-server && python3 -m venv .venv && .venv/bin/pip install mcp

# 3. Add to your project's .mcp.json (see examples/mcp.json)
# 4. Add the bootstrap to your project's CLAUDE.md (see examples/CLAUDE.md)
```

See `examples/` for ready-to-use configuration files.

## Architecture

```
pathfinder/agent/
├── mcp-server/
│   └── server.py            # MCP server — 17 tools
├── db/
│   ├── build.py             # Builds SQLite DB from JSON
│   └── pathfinder.db        # Built database (gitignored)
├── data/
│   ├── characters/
│   │   └── FORMAT.md        # Character sheet + state format specification
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
│   └── data/output/         # Generated JSON (source of truth for DB)
└── examples/
    ├── mcp.json             # Example .mcp.json for consuming projects
    └── CLAUDE.md            # Example CLAUDE.md bootstrap
```

## MCP Tools

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

### Included Guides (79 guides, 349 files, 14MB)

| Guide | Author | Original Source | Classes |
|-------|--------|-----------------|---------|
| Bell, Book, & Candle | Allerseelen | [Source](https://docs.google.com/document/d/1sRwsWVteboan4Gc5iIhuvCMMm5a0dd04GMK4HtjHFV8/edit) | Oracle |
| The Inquisitor's Symposium | Allerseelen | [Source](https://docs.google.com/document/d/1sFi5J6RODbKOYJglbELAM7bSLq9XCo7DO9QEtywZC5k/edit) | Inquisitor |
| The Investigator's Academy | Allerseelen | [Source](https://docs.google.com/document/d/1BkI5ph1ZDPRt8YrkCl9hG1VF8vHYbkC1nMRT9RcQGGE/edit) | Investigator |
| Follow My Voice | Allerseelen | [Source](https://docs.google.com/document/d/1D1_sHyxzowoTuCfWU8vGAUyP1gNjtw8EuFmY_UJO5bE/edit) | Mesmerist |
| The Occultist's Reliquary | Allerseelen | [Source](https://docs.google.com/document/d/1Trea8XI8StQrhF77jEiaACY7Fve8vqSManBU75FC6hU/edit) | Occultist |
| Rogues Gallery | Allerseelen | [Source](https://docs.google.com/document/d/1g2_5Z4Efx2Rxuj4q1nuFAh8AnWKezopD3WXyUn0lLi4/edit) | Vigilante |
| Going Nova | Allerseelen | [Source](https://docs.google.com/document/d/1VniMdd6X1noOA4KmBPzgflvyEWIHMl2tYawpjyFaZek/edit) | Kineticist |
| Guide to the Arcane Trickster | Significantotter | [Source](https://docs.google.com/document/d/1tpOQy_vA7SiaeU-YV5NnHJwVHpy-L9Spt-9RNYu-gSg/edit) | Arcane Trickster |
| Unlimited Mageworks (Sorcerer) | Iluzry | [Source](https://docs.google.com/document/d/17AbVMAIfWtRbXqavMevutmXhfuU-zYXY24yX01KFy74/edit) | Sorcerer |
| Building God's Grimoire (Sorcerer Spells) | Iluzry | [Source](https://docs.google.com/document/d/1_yWa7IJo2f8yD5MTSS7jAOGuo5xCRBjxBf2A2pMq1qs/edit) | Sorcerer |
| Blessed Be the Faithful (Cleric) | Iluzry | [Source](https://docs.google.com/document/d/15_OF0nNyOvMjjdcKkpWRHzWKHP4oZWPMcBWpKGT9e9s/edit) | Cleric |
| Bombs, Brews, and Blights (Alchemist) | Iluzry | [Source](https://docs.google.com/document/d/1uvX6Y8mHCdVFgTpLk9PjWU60bFFXSQEVKhGDl1knlpk/edit) | Alchemist |
| Magic Beyond Magic (Arcanist) | Iluzry | [Source](https://docs.google.com/document/d/1esXAlfclC1lDyJ2pOWzfYPkHs8ajQ79UV5SdvjYYMsY/edit) | Arcanist |
| The Show Must Go On (Bard) | Iluzry | [Source](https://docs.google.com/document/d/1zUWy_N76REjznrWlOzsDYy6Akast4bxS8z_RkLZgegQ/edit) | Bard |
| Becoming A Force of Nature (Druid) | Iluzry | [Source](https://docs.google.com/document/d/11_R80-e0ApO0g8bv2ZzQpb5V7NPIAtb7OKy5M6AGGQ0/edit) | Druid |
| Faerie Tricks & Big Sticks (Druid Spells) | Iluzry | [Source](https://docs.google.com/document/d/1wxWuKzXKIrdMEN8Pn5mr5vcasdtf0Gzj8A_8NehxtJE/edit) | Druid |
| Beyond The Blinding Fury (Barbarian) | Iluzry | [Source](https://docs.google.com/document/d/1fd7yBuCLWaytw8OFeZIXPCW0oUvPHwDGMDWWLoFe4xA/edit) | Barbarian |
| Guide to the Paladin/Antipaladin | Iluzry | [Source](https://docs.google.com/document/d/1lXA8U0D-dVZQXcHmq4lIS07-Mtz8uDpdSMNkyOW_BNY/edit) | Paladin |
| Friends On The Other Side (Shaman) | Iluzry | [Source](https://docs.google.com/document/d/1y3aijPPotHL-hnn7wMk3EZVYF3Qp7jxXjkCUZn-33Bs/edit) | Shaman |
| There Is No Spoon (Psychic) | Iluzry | [Source](https://docs.google.com/document/d/1EV1cwTL-RXscB3lqjsVAlxKN0VEPezjqKCmzX7ZKCVA/edit) | Psychic |
| The Art of Omnicide (Slayer) | Iluzry | [Source](https://docs.google.com/document/d/13Iu-XQ18JqInx7b90QP_biwCjkLviiMou4oSFEpfQYM/edit) | Slayer |
| Surpassing even The Boss (Gunslinger) | N. Jolly | [Source](https://docs.google.com/document/d/1En2ECuP1v63kTqGIUx5dpuhZQuoXl9Tc0UEj3P_xYN0/edit) | Gunslinger |
| Lord of Rage (Barbarian) | N. Jolly | [Source](https://docs.google.com/document/d/1plVgdYb5KYxtXiysgd_pzdK-37PCmz2u9VzpuvNPDdo/edit) | Barbarian |
| Chasing the Philosopher's Stone (Alchemist) | N. Jolly | [Source](https://docs.google.com/document/d/1hChbcEsEfQsR7NkwKlzO-GLYtrOtxlkGHpRQgKKZ5gc/edit) | Alchemist |
| Mastering the Elements (Kineticist) | N. Jolly | [Source](https://docs.google.com/document/d/1utgJVtJStEtZ8B923VWFYKIx6kbWQS_44zSMOb8rkT0/edit) | Kineticist |
| Synthesist Guide (Summoner) | N. Jolly | [Source](https://docs.google.com/document/d/17Z77UBaz6lmvqTJRMqnY7hzwYUpPPsmxLcW_1X6w5DU/edit) | Summoner |
| Piercing the Heavens (Warpriest) | N. Jolly | [Source](https://docs.google.com/document/d/1-nEbro_tLQ0ILxUd4vmht46-d6nbLk0RUbSRO5xUgvo/edit) | Warpriest |
| Marshmallow's Guide to the Fighter | Marshmallow | [Source](https://docs.google.com/document/d/1zM-CtViquLIQjpVgSI1Ot7zHAyIt_0U6dWvfGjA72lo/edit) | Fighter |
| Rogue Eidolon's Guide to Rogues | Rogue Eidolon | [Source](https://docs.google.com/document/d/13sCICmxwkq5yxdXVQqRr-H-SYrwUww13UFsKDcGJyJ4/edit) | Rogue |
| In Totality (Divine Spells) | platinumCheesecake | [Source](https://docs.google.com/document/d/1-5ZWOW3fZrJmJsWYU6ssaqWyhn-YWwoIlAQqfGzm774/edit) | Cleric, Oracle, Warpriest |
| Master Blaster Caster | Unknown | [Source](https://docs.google.com/document/d/17YnRW-LlKLUAW6cZ0EwndgpR35EDLk7jFI_0Z1ydtzU/edit) | Sorcerer, Wizard |
| Gestalt Character Guide | Community | [Source](https://docs.google.com/document/d/17Wv_-l25HMy3LORJ3JKSFjAf0P5Tjyhzdb6bT7oZviM/edit) | General |
| And 47 more... | Various | See `data/guides/INDEX.md` | Various |

## Game Data Sources

The SQLite database is built from two primary sources:

- **PSRD** (Pathfinder SRD) — Open Game License content extracted from the official SRD databases
- **Archives of Nethys (aonprd.com)** — Spell, feat, and archetype indexes scraped for names, URLs, and brief descriptions

All Pathfinder game mechanics content is published under the **Open Game License v1.0a** by Paizo Inc.

## License

The source code (Python scripts, MCP server, build tools) is licensed under the **Apache License 2.0** — see [LICENSE](LICENSE).

Guide content in `data/guides/` is the intellectual property of the respective authors listed above, included with attribution for non-commercial community use. It is **not** covered by the Apache license.

Pathfinder is a registered trademark of Paizo Inc. Game mechanics content is used under the Open Game License v1.0a.
