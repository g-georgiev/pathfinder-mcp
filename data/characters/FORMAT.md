# Character Sheet Format Reference

This document defines the standard format for character sheets in this plugin. Use it when creating or updating character files.

## Directory Structure

Each character is a directory under `data/characters/`:

```
data/characters/{name}/
├── sheet.md          # Main reference — stats, breakdowns, spell quick-reference
├── spells.md         # Full spell descriptions with tactical notes
├── features.md       # Class features, curses, revelations, racial traits, bloodline
├── feats.md          # Feat descriptions with prerequisites and interactions
├── backstory.md      # (optional) Character backstory, diary, notes
└── images/           # (optional) Character art
```

## sheet.md Structure

### Frontmatter

```yaml
---
name: Character Name
level: 3
classes: Class1 3 / Class2 3 (gestalt)    # or just "Fighter 5" for non-gestalt
race: Race Name
alignment: "neutral good"
deity: Deity Name
---
```

### Sections (in order)

1. **Title & Identity** — Name, level, race, class summary, deity, physical description
2. **Images** (optional) — Gallery row of character art
3. **Class Table** — Slot, class name, archetypes, hit die
4. **House Rules** (if any) — Campaign-specific rule modifications
5. **Quick Nav** — Two-column table: left = in-page anchors, right = reference file links
6. **Ability Scores** — Table with Base, Racial, Item, Total, Mod, Notes columns. Source of each bonus noted.
7. **Combat Stats**
   - **AC** — Breakdown table: each component (base, DEX, armor, shield, natural, deflection, etc.) with source
   - **HP** — Breakdown: hit dice, CON, feats, etc.
   - **Saves** — Table with Base, Ability, Item, Total. Note which save progression (good/poor) and source
   - **Special saves** — Line noting conditional save bonuses, SR, immunities. Link to source feat/feature
   - **Offense** — BAB, Initiative (with breakdown), Speed (with modifications), CMB, CMD (with breakdown)
8. **Skills** — Table with Total, Ranks, Ability mod, Class skill bonus, Other bonus, Other Source. Show ranks spent vs available.
9. **Feats** — Table with Level taken, linked feat name, quick effect, notes. Mark planned feats with `*(planned)*`.
10. **Character Traits** — Table with linked name and effect.
11. **Class Features — Quick Reference** — Subsections per class/source:
    - Curses, mysteries, revelations, bloodline powers, etc.
    - Each entry: level, linked name, one-line effect, source (chosen/archetype/etc.)
    - Mark planned features with `*(planned)*`
    - Future progression noted inline where relevant
12. **Racial Abilities** — Table with trait, effect, what it replaces (if alternate)
13. **Spellcasting** (one section per casting class)
    - CL, base DC formula, special notes (SR bonuses, arcana effects)
    - Slots per day table
    - Spell tables per level: linked name, action, range, duration, one-line effect, source
    - Mark future spell levels with `*(planned)*`

### Formatting Rules

- **Traceability**: Every derived number shows its math. AC 16 = 10 + 2 DEX + 4 Mage Armor. Don't just state totals.
- **Links**: Every spell, feat, and feature name links to its detail in the corresponding reference file: `[Spell Name](spells.md#spell-name)`
- **Planned vs current**: Anything not available at current level: `*(planned)*`
- **Source attribution**: Feats show level taken. Spells show source (chosen, bloodline bonus, curse bonus, archetype). Skills show what contributes to "other" bonuses.
- **Bold totals**: Use `**bold**` for final computed values in tables.
- **House rules**: Note inline where a house rule affects a calculation, e.g. `*(house rule: DEX replaces STR)*`

## spells.md Structure

```markdown
# {Name} — Spell Reference

[← Back to Sheet](sheet.md)

---

## {Class} Spells

### {Spell Name}

| | |
|---|---|
| **School** | School (subschool) [descriptor] |
| **Level** | Class1 N, Class2 N |
| **Casting Time** | 1 standard action |
| **Components** | V, S, M (material) |
| **Range** | Close / Medium / Long / Touch / Personal |
| **Target/Area/Effect** | ... |
| **Duration** | ... |
| **Save** | None / Will negates / Reflex half |
| **SR** | Yes / No |

Full description text. Include all mechanical details.

*Italicized tactical notes: why this spell matters, how it interacts with other abilities, effective values at current CL.*

[← Sheet](sheet.md)

---
```

- Group spells by casting class (## Oracle Spells, ## Sorcerer Spells)
- Include ALL spells from the main sheet — current and planned
- Tactical notes are optional but valuable — explain interactions, effective damage, optimal use cases
- Back-to-sheet link after every spell

## features.md Structure

```markdown
# {Name} — Class Features & Traits Reference

[← Back to Sheet](sheet.md)

---

## {Category}

### {Feature Name}

*(Planned — L7)* ← if not yet available

**Source**: Where this comes from (archetype, mystery, bloodline, etc.)
**Type**: Su / Ex / Sp

Full description text with all mechanical details.

*Italicized notes on interactions, effective values, build synergies.*

[← Sheet](sheet.md)

---
```

Categories (in order):
1. Character Traits
2. Racial Traits
3. Oracle Curses / Class-specific mechanics
4. Revelations / Class feature choices
5. Bloodline / Mystery / Domain powers
6. Other class features

## feats.md Structure

```markdown
# {Name} — Feats Reference

[← Back to Sheet](sheet.md)

---

### {Feat Name}

*(Planned — L5)* ← if not yet taken

| | |
|---|---|
| **Type** | General / Combat / Metamagic / etc. |
| **Source** | Book name |
| **Prerequisites** | Listed prerequisites |

**Benefit**: Full benefit text.

**Interactions**: (if relevant)
- How it interacts with other character abilities
- Effective values at current level

*Italicized build notes.*

**House rule**: (if any prerequisite waived or rule modified)

[← Sheet](sheet.md)

---
```

## Data Lookup Process

When creating a character sheet, for every spell, feat, and feature:

1. **Search the local DB** using MCP tools with `expand=True`
2. **Check completeness** — if the description is a one-line stub, it needs enrichment
3. **Web search** aonprd.com or d20pfsrd.com for the full text
4. **Cache** the complete data back to DB via `cache_entry`
5. **Write** the full description to the appropriate reference file

Never write a spell/feat entry with just a name and no description. The whole point of the reference files is that the user can look up what things do without leaving the sheet.

## Gestalt Characters

For gestalt builds:
- List both classes in the class table with slot numbers
- Use the higher HD, better save progression, and better BAB
- Class features stack (both classes' features apply)
- Spellcasting sections are separate per class
- Skills use the better skill ranks per level
