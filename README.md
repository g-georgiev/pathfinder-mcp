# Pathfinder 1e Advisor — Claude Code Plugin

A Claude Code plugin that turns Claude into an expert Pathfinder 1st Edition advisor. Backed by a local SQLite database of comprehensive game data, an MCP server for precision queries, and a curated library of community optimization guides.

## What It Does

- **Rules lookup** — Search spells, feats, classes, archetypes, items, and more from a local database of ~13,000 entries with full-text search
- **Character sheets** — Standardized multi-file character sheets with full stat breakdowns, spell/feat/feature reference files, and live combat state tracking
- **Build advice** — Recommendations backed by community optimization guides and game data
- **Combat assistance** — Apply buffs/conditions, calculate modified stats, generate Discord dice commands
- **Prerequisite checking** — Verify feat prerequisites and archetype compatibility against character stats
- **Read-through cache** — Missing data is fetched from aonprd.com/d20pfsrd.com and cached locally for future use

## Setup

```bash
# Install the plugin
claude --plugin-dir /path/to/pathfinder/agent

# Build the SQLite database from JSON data (first time only)
python3 db/build.py

# The MCP server venv needs the mcp package
cd mcp-server && python3 -m venv .venv && .venv/bin/pip install mcp
```

## Architecture

```
pathfinder/agent/
├── plugin.json              # Plugin manifest
├── .mcp.json                # MCP server configuration
├── .claude/rules/           # Advisor behavior, MCP tools, character conventions
├── db/
│   ├── build.py             # Builds SQLite DB from JSON
│   └── pathfinder.db        # Built database (gitignored)
├── mcp-server/
│   └── server.py            # MCP server — 14 tools for game data queries
├── data/
│   ├── characters/
│   │   └── FORMAT.md        # Character sheet + state format specification
│   └── guides/              # Community optimization guides (see Sources below)
├── agents/
│   └── character-builder.md # File generation agent
├── skills/
│   └── create-character/    # /create-character skill
└── scripts/
    ├── src/                 # Data pipeline (PSRD + aonprd extraction & merge)
    └── data/output/         # Generated JSON (source of truth for DB)
```

## Guide Sources & Attribution

The `data/guides/` directory contains optimization guides written by the Pathfinder community. These guides are publicly shared resources created to help players build better characters. They are included here in restructured form as a knowledge base, with full attribution to their original authors.

**If you are an author listed below and would like your content removed from this repository, please open an issue or contact the maintainer directly. Your content will be removed promptly.**

### Included Guides (38 guides, 258 files, 7.1MB)

| Guide | Author | Original Source | Classes |
|-------|--------|-----------------|---------|
| Bell, Book, & Candle | Allerseelen | [Google Doc](https://docs.google.com/document/d/1sRwsWVteboan4Gc5iIhuvCMMm5a0dd04GMK4HtjHFV8/edit) | Oracle |
| The Inquisitor's Symposium | Allerseelen | [Google Doc](https://docs.google.com/document/d/1sFi5J6RODbKOYJglbELAM7bSLq9XCo7DO9QEtywZC5k/edit) | Inquisitor |
| The Investigator's Academy | Allerseelen | [Google Doc](https://docs.google.com/document/d/1BkI5ph1ZDPRt8YrkCl9hG1VF8vHYbkC1nMRT9RcQGGE/edit) | Investigator |
| Guide to the Arcane Trickster | Significantotter | [Google Doc](https://docs.google.com/document/d/1tpOQy_vA7SiaeU-YV5NnHJwVHpy-L9Spt-9RNYu-gSg/edit) | Arcane Trickster |
| Surpassing even The Boss | N. Jolly | [Google Doc](https://docs.google.com/document/d/1En2ECuP1v63kTqGIUx5dpuhZQuoXl9Tc0UEj3P_xYN0/edit) | Gunslinger |
| Pathfinder Prestige Class Guide | Unknown | [Google Doc](https://docs.google.com/document/d/1d_EuU-PVeU0MQWwZPpHQ5w_Rsk76uRDv6_jLyS4jyDM/edit) | Prestige Classes |
| Bombs, Brews, and Blights | Iluzry | [Google Doc](https://docs.google.com/document/d/1uvX6Y8mHCdVFgTpLk9PjWU60bFFXSQEVKhGDl1knlpk/edit) | Alchemist |
| Guide to Rogues | Rogue Eidolon | [Google Doc](https://docs.google.com/document/d/13sCICmxwkq5yxdXVQqRr-H-SYrwUww13UFsKDcGJyJ4/edit) | Rogue |
| Magic Beyond Magic | Iluzry | [Google Doc](https://docs.google.com/document/d/1esXAlfclC1lDyJ2pOWzfYPkHs8ajQ79UV5SdvjYYMsY/edit) | Arcanist |
| Unlimited Mageworks | Iluzry | [Google Doc](https://docs.google.com/document/d/17AbVMAIfWtRbXqavMevutmXhfuU-zYXY24yX01KFy74/edit) | Sorcerer |
| Master Blaster Caster Guide | Unknown | [Google Doc](https://docs.google.com/document/d/17YnRW-LlKLUAW6cZ0EwndgpR35EDLk7jFI_0Z1ydtzU/edit) | Sorcerer, Wizard |
| Blessed Be the Faithful | Iluzry | [Google Doc](https://docs.google.com/document/d/15_OF0nNyOvMjjdcKkpWRHzWKHP4oZWPMcBWpKGT9e9s/edit) | Cleric |
| Magic Items by Build | BrotherPatrick | [Google Doc](https://docs.google.com/document/d/1uQlSAhs_s0mnWkCiQPbyJaaZVVkWcBlnnYl__fnuAzg/edit) | General |
| Gestalt Character Guide | Community | [Google Doc](https://docs.google.com/document/d/17Wv_-l25HMy3LORJ3JKSFjAf0P5Tjyhzdb6bT7oZviM/edit) | Gestalt |
| Getting X to Y | Unknown | [Google Doc](https://docs.google.com/document/d/1o91Z-s0R7Vf2Ujj1lFqGC5W--9JOyU0I6uC9XRIR5to/edit) | General |
| Tips and Traits | Unknown | [Google Doc](https://docs.google.com/document/d/1dVQA-uI740Hh8vq-zsnbHV6UwJg-4QKlpmkxBEmCdhA/edit) | General |
| The Armamentarium | Unknown | [Google Doc](https://docs.google.com/document/d/1ERhx5kiVaTRSPX1Uy9h3uWZieqPsDNoiT9TkKTC2qxk/edit) | General |
| Building God's Grimoire | Iluzry | [Google Doc](https://docs.google.com/document/d/1_yWa7IJo2f8yD5MTSS7jAOGuo5xCRBjxBf2A2pMq1qs/edit) | Sorcerer |
| In Totality | platinumCheesecake | [Google Doc](https://docs.google.com/document/d/1-5ZWOW3fZrJmJsWYU6ssaqWyhn-YWwoIlAQqfGzm774/edit) | Cleric, Oracle, Warpriest |
| Marshmallow's Guide to the Fighter | Marshmallow | [Google Doc](https://docs.google.com/document/d/1zM-CtViquLIQjpVgSI1Ot7zHAyIt_0U6dWvfGjA72lo/edit) | Fighter |
| Guide to the Paladin/Antipaladin | Iluzry | [Google Doc](https://docs.google.com/document/d/1lXA8U0D-dVZQXcHmq4lIS07-Mtz8uDpdSMNkyOW_BNY/edit) | Paladin, Antipaladin |
| Deadeye's Archery Paladin | Deadeye | [Google Doc](https://docs.google.com/document/d/1ID4_wGGCEsDsNGbDzn3hEfci-R1hq6WeT7IdEB4FxWU/edit) | Paladin |
| Lord of Rage: Guide to the Barbarian | N. Jolly | [Google Doc](https://docs.google.com/document/d/1plVgdYb5KYxtXiysgd_pzdK-37PCmz2u9VzpuvNPDdo/edit) | Barbarian |
| Beyond The Blinding Fury | Iluzry | [Google Doc](https://docs.google.com/document/d/1fd7yBuCLWaytw8OFeZIXPCW0oUvPHwDGMDWWLoFe4xA/edit) | Barbarian |
| BARBARIAN AM SMASH | Trinam | [Google Doc](https://docs.google.com/document/d/1Ump_KFzNoD7x6aJ9ywGank5G9DzSVlef28bBbjuIq2U/edit) | Barbarian |
| The Show Must Go On | Iluzry | [Google Doc](https://docs.google.com/document/d/1zUWy_N76REjznrWlOzsDYy6Akast4bxS8z_RkLZgegQ/edit) | Bard |
| All the World's a Stage | Unknown | [Google Doc](https://docs.google.com/document/d/1ogz8HL6GeguT-tN3-6HxXiF_G7mg_tyAQ59V9kPg6g4/edit) | Bard |
| Guide to the Buffer Bard | Unknown | [Google Doc](https://docs.google.com/document/d/1b1hq_xhfCFjtAyjJMKrdtxRbtDEC1kNm6ZYfvS6HqIw/edit) | Bard |
| Becoming A Force of Nature | Iluzry | [Google Doc](https://docs.google.com/document/d/11_R80-e0ApO0g8bv2ZzQpb5V7NPIAtb7OKy5M6AGGQ0/edit) | Druid |
| Faerie Tricks & Big Sticks | Iluzry | [Google Doc](https://docs.google.com/document/d/1wxWuKzXKIrdMEN8Pn5mr5vcasdtf0Gzj8A_8NehxtJE/edit) | Druid |
| Prometeus Guide to the Druid | Prometeus | [Google Doc](https://docs.google.com/document/d/1PXamF43boZgYtCUlyJAMojfrPaAdYyjPOaGOo1vfqdM/edit) | Druid |
| Shutting Down Enemies | Unknown | [Google Doc](https://docs.google.com/document/d/1YkARuboGbaCVdOpcgoA0epQFqBlCygzzUsgaBdba9BE/edit) | Witch |
| Owl's Guide to Witches | Owl | [Google Doc](https://docs.google.com/document/d/1tYE8wheVXGAitQzgLW15X8RoPI8-d27o_GTgUXSVHZ0/edit) | Witch |
| Myrrh, Frankincense, and Steel | Kurald Galain | [Google Doc](https://docs.google.com/document/d/1jaxkoUJY6hWg5hrNi3KDk42nzq3xXeMCfQLVp55aeRY/edit) | Magus |
| Forger's Supplemental Guide to the Magus | Forger | [Google Doc](https://docs.google.com/document/d/1sQxhtYSMvzoAcVkDkn94vbDWP5pJtKwsOFCWEe_NzZg/edit) | Magus |
| Jam's Blended Archetype Guide: The Monk | JAM | [Google Doc](https://docs.google.com/document/d/1-IdBUQ7A8FNa_R_caBNFXdaurdWgAaE4qpzzU_AcRBI/edit) | Monk |
| Master of Many Styles | Unknown | [Google Doc](https://docs.google.com/document/d/1r-Wh9DgkEwF3Wtj8QMDTdF2kVpQVCS5BCjU2vPcG7Wk/edit) | Monk |
| Optimizing your Qinggong Monk | Unknown | [Google Doc](https://docs.google.com/document/d/15c_ACgqmpVPY82d4-WSWHGmZXyjiVW9D6311QOneU0U/edit) | Monk |

## Game Data Sources

The SQLite database is built from two primary sources:

- **PSRD** (Pathfinder SRD) — Open Game License content extracted from the official SRD databases
- **Archives of Nethys (aonprd.com)** — Spell, feat, and archetype indexes scraped for names, URLs, and brief descriptions

All Pathfinder game mechanics content is published under the **Open Game License v1.0a** by Paizo Inc.

## License

The plugin source code (Python scripts, MCP server, build tools, agent/skill definitions) is licensed under the **Apache License 2.0** — see [LICENSE](LICENSE).

Guide content in `data/guides/` is the intellectual property of the respective authors listed above, included with attribution for non-commercial community use. It is **not** covered by the Apache license.

Pathfinder is a registered trademark of Paizo Inc. Game mechanics content is used under the Open Game License v1.0a.
