# Optimization Guides

The `data/guides/` directory contains 20 community optimization guides covering classes, spells, feats, items, and build strategies. Use these when answering build questions, recommending options, or planning character progression.

## How to Find the Right Guide

Each guide directory has either an `index.md` (multi-file guide with sections) or a `guide.md` (single file). Both have YAML frontmatter with `classes` and `topics` fields.

**To find guides for a class or topic:**
```
grep -rl "oracle" data/guides/*/index.md data/guides/*/guide.md
```

**To find a specific recommendation within guides:**
```
grep -ril "sidestep secret" data/guides/
```

## Guide Index

### Class Guides (multi-file, sectioned)

| Directory | Class | Author | Key Sections |
|-----------|-------|--------|--------------|
| `oracle-allerseelen/` | Oracle | Allerseelen | mysteries, curses, spells, feats, roles, archetypes, multiclass, builds |
| `inquisitor-allerseelen/` | Inquisitor | Allerseelen | domains, spells, feats, combat styles, archetypes, multiclass, builds |
| `investigator-allerseelen/` | Investigator | Allerseelen | extracts, talents, feats, archetypes, builds |
| `arcane-trickster-significantotter/` | Arcane Trickster | Significantotter | prerequisites, spells, feats, builds |

These have separate files per section (e.g. `spells.md`, `feats.md`, `mysteries.md`). Read only the section you need.

### Class Guides (single file)

| Directory | Class | Author |
|-----------|-------|--------|
| `sorcerer-iluzry/` | Sorcerer | Iluzry |
| `sorcerer-spells-iluzry/` | Sorcerer (spells) | Iluzry |
| `cleric-iluzry/` | Cleric | Iluzry |
| `alchemist-iluzry/` | Alchemist | Iluzry |
| `arcanist-iluzry/` | Arcanist | Iluzry |
| `gunslinger-njolly/` | Gunslinger | N. Jolly |
| `fighter-marshmallow/` | Fighter | Marshmallow |
| `rogue-rogueeidolon/` | Rogue | Rogue Eidolon |
| `blaster-caster/` | Sorcerer/Wizard (blasting) | Unknown |

These are large single files. Use grep to find the relevant section rather than reading the entire file.

### General Guides (single file)

| Directory | Topic | Author |
|-----------|-------|--------|
| `gestalt-guide/` | Gestalt character building | Community |
| `cleric-oracle-warpriest-spells/` | Divine spell ratings | platinumCheesecake |
| `prestige-classes-guide/` | Prestige class ratings | Unknown |
| `ability-scores-xty/` | Getting X to Y (stat substitution) | Unknown |
| `magic-items-brotherpatrick/` | Magic items by build type | BrotherPatrick |
| `wondrous-items-guide/` | Wondrous item ratings | Unknown |
| `traits-guide/` | Character trait ratings | Unknown |

## When to Use Guides

**Use guides when:**
- The user asks for build advice, feat/spell recommendations, or "what should I take?"
- Evaluating options (is Mystery X better than Mystery Y for this build?)
- Planning a level-up or multi-level progression
- Building a new character from a concept
- Comparing archetypes, bloodlines, domains, or other class options

**How to use them:**
1. Identify the relevant class(es) from the user's question
2. Grep or read the appropriate guide sections
3. Cross-reference guide recommendations with the DB (search for the actual feat/spell data)
4. Combine guide opinion with game mechanics for a complete answer
5. Cite the guide and author when quoting ratings or recommendations

**Don't just parrot the guide.** The guides are one expert's opinion — synthesize their recommendations with the character's specific build, house rules, party composition, and campaign context. If a guide rates something poorly but it fits the character's theme or fills a party gap, say so.

## Rating Systems

Most guides use a color or numeric rating system. Common patterns:
- **Iluzry**: Numeric (1/5 to 6/5), higher is better
- **Allerseelen**: Color-coded (blue = excellent, green = good, orange = situational, red = avoid)
- **Others**: Vary, but usually explained at the top of the guide

When conveying ratings, include the guide's reasoning, not just the score.

## Build Planning Workflow

When helping plan a character build from concept to completion:

1. **Clarify the concept** — class, role (melee/caster/support), theme, level range
2. **Read the role/overview section** of the relevant class guide for strategic direction
3. **Race selection** — check the guide's race section + gestalt guide if applicable
4. **Core choices** — mystery/bloodline/domain from the guide's analysis
5. **Feat progression** — guide's feat section cross-referenced with `check_feat_prerequisites`
6. **Spell selection** — guide's spell section + spell-specific guides if available
7. **Equipment** — magic items guide + class guide equipment section
8. **Validate** — check all prerequisites, stacking, and math against the DB
