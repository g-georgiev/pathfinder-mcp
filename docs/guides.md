# Optimization Guides

The `data/guides/` directory contains 79 community optimization guides covering classes, spells, feats, items, and build strategies. Use these when answering build questions, recommending options, or planning character progression.

## How to Find the Right Guide

**Start with the index:** Read `data/guides/INDEX.md` for a complete listing of all guides organized by class and topic, with direct links to entry points.

Each guide directory has either an `index.md` (multi-file guide with sections) or a `guide.md` (single file). Both have YAML frontmatter with `classes` and `topics` fields.

**To find a specific recommendation within guides:**
```
grep -ril "sidestep secret" data/guides/
```

## When to Use Guides

**Use guides when:**
- The user asks for build advice, feat/spell recommendations, or "what should I take?"
- Evaluating options (is Mystery X better than Mystery Y for this build?)
- Planning a level-up or multi-level progression
- Building a new character from a concept
- Comparing archetypes, bloodlines, domains, or other class options

**How to use them:**
1. Identify the relevant class(es) from the user's question
2. Read `data/guides/INDEX.md` to find the right guide(s)
3. Grep or read the appropriate guide sections
4. Cross-reference guide recommendations with the DB (search for the actual feat/spell data)
5. Combine guide opinion with game mechanics for a complete answer
6. Cite the guide and author when quoting ratings or recommendations

**Multiple perspectives:** Most popular classes have 2-3 guides by different authors. When guides disagree, present both perspectives and explain the tradeoff. Don't default to one author's opinion.

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
