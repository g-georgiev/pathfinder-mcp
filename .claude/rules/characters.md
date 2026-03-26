# Character Sheet Conventions

Each character is a **directory** under `data/characters/` containing multiple linked markdown files:

```
data/characters/{name}/
├── sheet.md        # Main reference — stats, breakdowns, spell quick-reference
├── spells.md       # Full spell descriptions (casting time, range, duration, save, full text)
├── features.md     # Class features, curses, revelations, racial traits, bloodline powers
├── feats.md        # Feat descriptions with prerequisites and interactions
└── state.md        # (optional) Live combat state — buffs, conditions, resources
```

See `data/characters/FORMAT.md` for the complete format specification including state.md structure.

## Formatting Rules

- **Traceability**: Every derived number traces to its source (e.g. AC 16 = 10 base + 2 DEX + 4 Mage Armor). Show the math.
- **Spell tables**: Main sheet has one-line summaries (action, range, duration, effect). Full descriptions with tactical notes in `spells.md`.
- **Linked references**: Use `[Spell Name](spells.md#spell-name)` links throughout. Every mention of a spell, feat, or feature should link to its full description.
- **Back-to-sheet links**: Every section in reference files ends with `[← Sheet](sheet.md)` for easy navigation.
- **Planned vs current**: Anything not yet available at current level is marked with `*(planned)*`.
- **Source attribution**: Feats show which level they were taken. Spells show their source (chosen, bloodline bonus, curse bonus, archetype). Skills show what contributes to each bonus.
- **Frontmatter**: `sheet.md` has YAML frontmatter with name, level, classes, race for quick identification.

## Data Completeness

Many DB entries are stubs — flagged with `_stub: true` when queried with `expand=True`. When writing or updating character sheets:
1. Query with `expand=True` and check the `_stub` flag
2. If `_stub: true`, web fetch the entry's `url` for full data
3. Cache the enriched data via `cache_entry` (replaces the stub permanently)
4. Write the complete description to the character's reference file

Never use stub text in character sheets. Always enrich first.

## Personal Data

Campaign-specific data (characters, guides, house rules) lives in a separate directory/repo. Check for a sibling `personal/` directory or the user's own CLAUDE.md for campaign house rules. Character sheets are stored under the personal data directory, not in this plugin.
