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

### Included Guides (79 guides, 701 files, 15MB)

| Guide | Author | Original Source | Classes |
|-------|--------|-----------------|---------|
| A Guide to the Veneficus Witch | Unknown | [Source](https://docs.google.com/document/d/1wZmgJe8jnUCGmje-vqMQivpORDjJMs6VeF-TDJJLi-U/edit) | Witch |
| A Witch's Guide to Shutting Down Enemies | Unknown | [Source](https://docs.google.com/document/d/1YkARuboGbaCVdOpcgoA0epQFqBlCygzzUsgaBdba9BE/edit) | Witch |
| All the World's a Stage: Guide to the Bard | Unknown | [Source](https://docs.google.com/document/d/1ogz8HL6GeguT-tN3-6HxXiF_G7mg_tyAQ59V9kPg6g4/edit) | Bard |
| Archmage Variel's Guide to the Shifter | Archmage Variel | [Source](https://docs.google.com/document/d/1uhp5v8_tu_rLMX4T266g4rh-ceu_u-8kCZHjFFNHJcY/edit) | Shifter |
| BARBARIAN AM SMASH: A Practical Guide to Breaking Faces | Trinam | [Source](https://docs.google.com/document/d/1Ump_KFzNoD7x6aJ9ywGank5G9DzSVlef28bBbjuIq2U/edit) | Barbarian |
| BLOW THEM TO SMITHEREENS! Master Blaster Caster Guide | Unknown | [Source](https://docs.google.com/document/d/17YnRW-LlKLUAW6cZ0EwndgpR35EDLk7jFI_0Z1ydtzU/edit) | Sorcerer, Wizard |
| Becoming A Force of Nature: Iluzry's Guide to the Druid | Iluzry | [Source](https://docs.google.com/document/d/11_R80-e0ApO0g8bv2ZzQpb5V7NPIAtb7OKy5M6AGGQ0/edit) | Druid |
| Beginner's Basics to the Master of Many Styles | Unknown | [Source](https://docs.google.com/document/d/1r-Wh9DgkEwF3Wtj8QMDTdF2kVpQVCS5BCjU2vPcG7Wk/edit) | Monk |
| Being Sherlock Holmes: A Gentleman's Guide to the Investigator | Unknown | [Source](https://docs.google.com/document/d/1US1RDLezrR7C7bTjm_7Q9cta6bYi_slsE6zc1ndf7eg/edit) | Investigator |
| Bell, Book, & Candle: A Guide to the Pathfinder Oracle | Allerseelen | [Source](https://docs.google.com/document/d/1sRwsWVteboan4Gc5iIhuvCMMm5a0dd04GMK4HtjHFV8/edit) | Oracle |
| Beyond The Blinding Fury: Iluzry's Guide to the Barbarian | Iluzry | [Source](https://docs.google.com/document/d/1fd7yBuCLWaytw8OFeZIXPCW0oUvPHwDGMDWWLoFe4xA/edit) | Barbarian |
| Blessed Be the Faithful: Guide to Clerics | Iluzry | [Source](https://docs.google.com/document/d/15_OF0nNyOvMjjdcKkpWRHzWKHP4oZWPMcBWpKGT9e9s/edit) | Cleric |
| Bodhi's Guide to the Optimal Inquisitor | Bodhi | [Source](https://docs.google.com/document/d/1gFK_A8YV84hMUMXjxvCLFTnGO2GF7CMQiGIYyAQ2kns/edit) | Inquisitor |
| Bombs, Brews, and Blights: Guide to the Alchemist | Iluzry | [Source](https://docs.google.com/document/d/1uvX6Y8mHCdVFgTpLk9PjWU60bFFXSQEVKhGDl1knlpk/edit) | Alchemist |
| Brawlers: Debuffing with Style | Unknown | [Source](https://docs.google.com/document/d/1uhCZmbd8MUoro9RbeUQPuJBQvIjmIzEEKza8R0JBVKs/edit) | Brawler |
| Building God's Grimoire: Guide to Sorcerer Spells | Iluzry | [Source](https://docs.google.com/document/d/1_yWa7IJo2f8yD5MTSS7jAOGuo5xCRBjxBf2A2pMq1qs/edit) | Sorcerer |
| Cartmanbeck's Guide to the Iron Caster | Cartmanbeck | [Source](https://docs.google.com/document/d/1G1oa8hQif08qqRdEyMnDVVFAoBN_53uhNcJc4wArQxs/edit) | Fighter |
| Channeling the Cosmos: A Guide to the Oracle | Unknown | [Source](https://docs.google.com/document/d/1WdtrZCESRmVfljXY196wMrMLTnS8Uzk4DEk3oQdVZok/edit) | Oracle |
| Chasing the Philosopher's Stone: N. Jolly's Alchemist Guide | N. Jolly | [Source](https://docs.google.com/document/d/1hChbcEsEfQsR7NkwKlzO-GLYtrOtxlkGHpRQgKKZ5gc/edit) | Alchemist |
| Dawar's Guide to the Arcanist | Dawar | [Source](https://docs.google.com/document/d/1EjwZkuIDLUO4M_snPEeUdMWBIBz1jFk28e9HeEjUDu8/edit) | Arcanist |
| Deadeye's Servant: Guide to the Archery Paladin | Deadeye | [Source](https://docs.google.com/document/d/1ID4_wGGCEsDsNGbDzn3hEfci-R1hq6WeT7IdEB4FxWU/edit) | Paladin |
| Faerie Tricks & Big Sticks: Iluzry's Guide to Druid Spells | Iluzry | [Source](https://docs.google.com/document/d/1wxWuKzXKIrdMEN8Pn5mr5vcasdtf0Gzj8A_8NehxtJE/edit) | Druid |
| Follow My Voice: Allerseelen's Guide to the Mesmerist | Allerseelen | [Source](https://docs.google.com/document/d/1D1_sHyxzowoTuCfWU8vGAUyP1gNjtw8EuFmY_UJO5bE/edit) | Mesmerist |
| Forger's Supplemental Guide to the Updated Magus | Forger | [Source](https://docs.google.com/document/d/1sQxhtYSMvzoAcVkDkn94vbDWP5pJtKwsOFCWEe_NzZg/edit) | Magus |
| Friends On The Other Side: Iluzry's Guide to the Shaman | Iluzry | [Source](https://docs.google.com/document/d/1y3aijPPotHL-hnn7wMk3EZVYF3Qp7jxXjkCUZn-33Bs/edit) | Shaman |
| Getting X to Y: Guide to Ability Scores | Unknown | [Source](https://docs.google.com/document/d/1o91Z-s0R7Vf2Ujj1lFqGC5W--9JOyU0I6uC9XRIR5to/edit) | General |
| Getting into Someone Else's Skin: N. Jolly's Synthesist Guide | N. Jolly | [Source](https://docs.google.com/document/d/17Z77UBaz6lmvqTJRMqnY7hzwYUpPPsmxLcW_1X6w5DU/edit) | Summoner |
| Ginsu Master: Ranger's Guide to Two Weapon Fighting | Unknown | [Source](https://docs.google.com/document/d/1JRq3ywFhF3BsJH1tTj5JgRhN2gvwiyUaLUgvDYv-gCI/edit) | Ranger |
| Going Nova: Allerseelen Guide to the Kineticist | Allerseelen | [Source](https://docs.google.com/document/d/1VniMdd6X1noOA4KmBPzgflvyEWIHMl2tYawpjyFaZek/edit) | Kineticist |
| Guide to the Buffer Bard | Unknown | [Source](https://docs.google.com/document/d/1b1hq_xhfCFjtAyjJMKrdtxRbtDEC1kNm6ZYfvS6HqIw/edit) | Bard |
| Guide to the Outflanking Hunter | Unknown | [Source](https://docs.google.com/document/d/1C1B8p3doNyII9_XB_2ROPEpvJL5J1mYJk8mbJqHLOBk/edit) | Hunter |
| How to Become the Lord of Rage: N. Jolly's Guide to the Barbarian | N. Jolly | [Source](https://docs.google.com/document/d/1plVgdYb5KYxtXiysgd_pzdK-37PCmz2u9VzpuvNPDdo/edit) | Barbarian |
| How to be Metal: Skald Guide | Unknown | [Source](https://docs.google.com/document/d/1lHp_ioueUwkoZzxBKYg4ha3uVV07K8RNngL4J5EqtYU/edit) | Skald |
| I am Vengeance, I am the Night: Vigilante Guide | Unknown | [Source](https://docs.google.com/document/d/18z70ARGsGF92VbV0Ithx_4PpwTQXDqUw0Ph1UvqLfVU/edit) | Vigilante |
| Iluzry's Guide to the Paladin/Antipaladin | Iluzry | [Source](https://docs.google.com/document/d/1lXA8U0D-dVZQXcHmq4lIS07-Mtz8uDpdSMNkyOW_BNY/edit) | Paladin, Antipaladin |
| In Totality: Guide to Cleric/Oracle/Warpriest Spells | platinumCheesecake | [Source](https://docs.google.com/document/d/1-5ZWOW3fZrJmJsWYU6ssaqWyhn-YWwoIlAQqfGzm774/edit) | Cleric, Oracle, Warpriest |
| Jam's Blended Archetype Guide: The Monk | JAM | [Source](https://docs.google.com/document/d/1-IdBUQ7A8FNa_R_caBNFXdaurdWgAaE4qpzzU_AcRBI/edit) | Monk |
| Leasing Your Body for Fun and Profit: Guide to the Medium | CockroachTeaParty | [Source](https://docs.google.com/document/d/18513dKdB74fbtloy7cKgCtJkHEsTrAa3SsS56LguMqQ/edit) | Medium |
| Lokotor's Gunslinger Guide | Lokotor | [Source](https://docs.google.com/document/d/1_aDDwhK-un7jjRJeSNHjqatraT5fdCI4A4D5xe-cs90/edit) | Gunslinger |
| Magic Beyond Magic: Guide to the Arcanist | Iluzry | [Source](https://docs.google.com/document/d/1esXAlfclC1lDyJ2pOWzfYPkHs8ajQ79UV5SdvjYYMsY/edit) | Arcanist |
| Marshmallow's Guide to the Fighter | Marshmallow | [Source](https://docs.google.com/document/d/1zM-CtViquLIQjpVgSI1Ot7zHAyIt_0U6dWvfGjA72lo/edit) | Fighter |
| Mastering the Elements: N. Jolly Guide to the Kineticist | N. Jolly | [Source](https://docs.google.com/document/d/1utgJVtJStEtZ8B923VWFYKIx6kbWQS_44zSMOb8rkT0/edit) | Kineticist |
| Myrrh, Frankincense, and Steel: Kurald Galain's Guide to the Magus | Kurald Galain | [Source](https://docs.google.com/document/d/1jaxkoUJY6hWg5hrNi3KDk42nzq3xXeMCfQLVp55aeRY/edit) | Magus |
| Nobody Expects a Guide to the Inquisitor | Unknown | [Source](https://docs.google.com/document/d/19N7y6cKFLAr2KMMiKc8A1XG6R4iOmwaNFS7iAs17zyU/edit) | Inquisitor |
| One B.A.M.F's Guide to the Bloodrager | Unknown | [Source](https://docs.google.com/document/d/1Vl_0wbMAK09qq083Lqs7k5CMP4ICv2_49Nat7pPWn4A/edit) | Bloodrager |
| Optimizing your Qinggong Monk | Unknown | [Source](https://docs.google.com/document/d/15c_ACgqmpVPY82d4-WSWHGmZXyjiVW9D6311QOneU0U/edit) | Monk |
| Owl's Guide to Witches | Owl | [Source](https://docs.google.com/document/d/1tYE8wheVXGAitQzgLW15X8RoPI8-d27o_GTgUXSVHZ0/edit) | Witch |
| Pathfinder First Edition Magic Items by Build | BrotherPatrick | [Source](https://docs.google.com/document/d/1uQlSAhs_s0mnWkCiQPbyJaaZVVkWcBlnnYl__fnuAzg/edit) | General |
| Pathfinder Gestalt Character Guide | Community | [Source](https://docs.google.com/document/d/17Wv_-l25HMy3LORJ3JKSFjAf0P5Tjyhzdb6bT7oZviM/edit) | General |
| Pathfinder Prestige Class Guide | Unknown | [Source](https://docs.google.com/document/d/1d_EuU-PVeU0MQWwZPpHQ5w_Rsk76uRDv6_jLyS4jyDM/edit) | General |
| Phantom of the OP-era: Guide to the Spiritualist | Unknown | [Source](https://docs.google.com/document/d/1u4SF3ZU20zl2eyuXzJuhPgj7eXkVaM6rmqB63y6vKPM/edit) | Spiritualist |
| Piercing the Heavens: N. Jolly's Guide to the Warpriest | N. Jolly | [Source](https://docs.google.com/document/d/1-nEbro_tLQ0ILxUd4vmht46-d6nbLk0RUbSRO5xUgvo/edit) | Warpriest |
| Prometeus Guide to the Druid | Prometeus | [Source](https://docs.google.com/document/d/1PXamF43boZgYtCUlyJAMojfrPaAdYyjPOaGOo1vfqdM/edit) | Druid |
| Raining Blood: The Bloodrager's Guide | Unknown | [Source](https://docs.google.com/document/d/1uV52XseHRUMKOM-fLF6oXwkF-bcmmPk93XR8u02-sYw/edit) | Bloodrager |
| Rogue Eidolon's Guide to Rogues | Rogue Eidolon | [Source](https://docs.google.com/document/d/13sCICmxwkq5yxdXVQqRr-H-SYrwUww13UFsKDcGJyJ4/edit) | Rogue |
| Rogues Gallery: Allerseelen's Guide to the Vigilante | Allerseelen | [Source](https://docs.google.com/document/d/1g2_5Z4Efx2Rxuj4q1nuFAh8AnWKezopD3WXyUn0lLi4/edit) | Vigilante |
| Seeing The Forest through The Trees: Ranger Guide | Unknown | [Source](https://docs.google.com/document/d/1l9XmMykBFrbYCNN47lAHvHnnCQj3i1cea0HLT3IeihU/edit) | Ranger |
| Significantotter’s Guide to the Arcane Trickster | Significantotter | [Source](https://docs.google.com/document/d/1tpOQy_vA7SiaeU-YV5NnHJwVHpy-L9Spt-9RNYu-gSg/edit) | Arcane Trickster, Rogue, Wizard |
| Surpassing even The Boss: N. Jolly's Guide to the Gunslinger | N. Jolly | [Source](https://docs.google.com/document/d/1En2ECuP1v63kTqGIUx5dpuhZQuoXl9Tc0UEj3P_xYN0/edit) | Gunslinger |
| THE COMPLETE Professor Q's Guide to the Pathfinder Wizard | Professor Q | [Source](https://docs.google.com/document/d/1mmafMuRRd3ubCMhCNmOomLUn_YvaVXiHwSyuC1YDrNc/edit) | Wizard |
| Tark's Big Holy Book of Clerical Optimization | Tark | [Source](https://docs.google.com/document/d/1h6-_4HvPvV-Tt7I67Gi_oPhgHmeDVA5SBl-WrJSgf5s/edit) | Cleric |
| Tark's Guide to Building Tag Team Champions (Summoner) | Tark | [Source](https://docs.google.com/document/d/1BVWY_NR5kJZAeGNYyvD5ljRs6whzFPDBCvOAryq2qcE/edit) | Summoner |
| The Armamentarium: Guide to Wondrous Items | Unknown | [Source](https://docs.google.com/document/d/1ERhx5kiVaTRSPX1Uy9h3uWZieqPsDNoiT9TkKTC2qxk/edit) | General |
| The Art of Omnicide: Iluzry's Guide to the Slayer | Iluzry | [Source](https://docs.google.com/document/d/13Iu-XQ18JqInx7b90QP_biwCjkLviiMou4oSFEpfQYM/edit) | Slayer |
| The Cavalier's Code | Unknown | [Source](https://docs.google.com/document/d/1uuAB8SfE5ssZLYwa1LuQQ4haz1tD1q28Iyl8XAdMNxY/edit) | Cavalier |
| The Cavalry Has Arrived | Unknown | [Source](https://docs.google.com/document/d/17pOyVpYRCHrYsNrOcLufRhBkoPgy2QD5iPNwN148BeU/edit) | Cavalier |
| The Inquisitor’s Symposium: A Guide to the Pathfinder Inquisitor | Allerseelen | [Source](https://docs.google.com/document/d/1sFi5J6RODbKOYJglbELAM7bSLq9XCo7DO9QEtywZC5k/edit) | Inquisitor |
| The Investigator’s Academy: A Guide to the Pathfinder Investigator | Allerseelen | [Source](https://docs.google.com/document/d/1BkI5ph1ZDPRt8YrkCl9hG1VF8vHYbkC1nMRT9RcQGGE/edit) | Investigator |
| The Muscle Wizard: A Guide to Greatness | Unknown | [Source](https://docs.google.com/document/d/10x042PGSyqX4JqHbYFf7vDsK1NCnhBT2ck8i1eG6kpc/edit) | Wizard |
| The Occultist's Reliquary: Allerseelen's Guide to the Occultist | Allerseelen | [Source](https://docs.google.com/document/d/1Trea8XI8StQrhF77jEiaACY7Fve8vqSManBU75FC6hU/edit) | Occultist |
| The Seer's Catalog: Shaman Guide | Unknown | [Source](https://docs.google.com/document/d/1Z7WB_ZPHgCs1tXht_QLKmCxLlpp8ku-dZrJ_Mx06kAo/edit) | Shaman |
| The Show Must Go On: Iluzry's Guide to the Bard | Iluzry | [Source](https://docs.google.com/document/d/1zUWy_N76REjznrWlOzsDYy6Akast4bxS8z_RkLZgegQ/edit) | Bard |
| There Is No Spoon: Iluzry's Guide to the Psychic | Iluzry | [Source](https://docs.google.com/document/d/1EV1cwTL-RXscB3lqjsVAlxKN0VEPezjqKCmzX7ZKCVA/edit) | Psychic |
| Tips and Traits: Guide to Pathfinder Traits | Unknown | [Source](https://docs.google.com/document/d/1dVQA-uI740Hh8vq-zsnbHV6UwJg-4QKlpmkxBEmCdhA/edit) | General |
| Treantmonk's Guide to Pathfinder Wizards | Treantmonk | [Source](https://docs.google.com/document/d/1VCY-VPRw0XIOjJLvwjySq4IKsU-jYc7rCNKpH7HRoWM/edit) | Wizard |
| Two Hands Are Better Than One: THF Fighter Guide | Unknown | [Source](https://docs.google.com/document/d/18hu5OjSAFCXdd2FtnUIMAbPq5taYQOe6ZOuidib0dlU/edit) | Fighter |
| Unchained Summons Guide | Unknown | [Source](https://docs.google.com/document/d/1flEJrpr3VIkc09cH_ZofizK_9Dy90YNR3VWC_rIRtJM/edit) | Summoner |
| Unlimited Mageworks: Guide to the Pathfinder 1e Sorcerer | Iluzry | [Source](https://docs.google.com/document/d/17AbVMAIfWtRbXqavMevutmXhfuU-zYXY24yX01KFy74/edit) | Sorcerer |
| kjb200's Update to Rogue Eidolon's Guide | kjb200 | [Source](https://docs.google.com/document/d/1i9VeolUtnRfxC28JIBPaQWQYs57wEvfq5XtEcOR6C0A/edit) | Rogue |

## Game Data Sources

The SQLite database is built from two primary sources:

- **PSRD** (Pathfinder SRD) — Open Game License content extracted from the official SRD databases
- **Archives of Nethys (aonprd.com)** — Spell, feat, and archetype indexes scraped for names, URLs, and brief descriptions

All Pathfinder game mechanics content is published under the **Open Game License v1.0a** by Paizo Inc.

## License

The plugin source code (Python scripts, MCP server, build tools, agent/skill definitions) is licensed under the **Apache License 2.0** — see [LICENSE](LICENSE).

Guide content in `data/guides/` is the intellectual property of the respective authors listed above, included with attribution for non-commercial community use. It is **not** covered by the Apache license.

Pathfinder is a registered trademark of Paizo Inc. Game mechanics content is used under the Open Game License v1.0a.
