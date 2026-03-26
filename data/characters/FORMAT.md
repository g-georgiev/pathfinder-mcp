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
   - **AC** — Breakdown table: each component (base, DEX, armor, shield, natural, deflection, etc.) with source. Include always-on bonuses (luck, insight from items) in the total, not as situational footnotes. Add tactical reminders for key reactive items (e.g. "Don't forget: Bracelet of Second Chances") near the stats they protect.
   - **HP** — Breakdown table with explicit line items: hit dice (note max at L1 + avg-up thereafter), CON, favored class bonus, Toughness, etc. Include a **Current wounds** line for tracking damage between sessions.
   - **Saves** — Table with Base, Ability, Item (broken out: resistance, competence, luck, etc.), Total. Note which save progression (good/poor) and source. Add tactical reminders for key reactive items near saves too.
   - **Special saves** — Line noting conditional save bonuses, SR, immunities. Link to source feat/feature (e.g. Evasion, Stalwart, Shake It Off).
   - **Offense** — BAB, Initiative (with breakdown), Speed (with modifications), CMB, CMD (with breakdown)
   - **Attacks** — Full attack stat block: table with each iterative (Attack, AB, Damage, Crit). Below the table: AB breakdown formula, Damage breakdown formula. Then list common buff modifiers (Deadly Aim, Rapid Shot, Bane, etc.) with their AB/damage adjustments. Include threat range and AoO details if relevant.
8. **Skills** — Table with Total, Ranks, Ability mod, Class skill bonus, Other bonus, Other Source. Show ranks spent vs available. Bake always-on bonuses (e.g. Pale Green Prism +1 competence, luck bonuses) into the totals rather than listing them as situational footnotes — note them in the Other Source column. Include item bonuses (e.g. skill-boosting gloves) in the total.
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
    - Source column: "Known" for standard class spells, but also track item sources like "Page of Spell Knowledge", "Ring of Spell Storing", etc.
    - Mark future spell levels with `*(planned)*`
    - After spell tables: **Item-Based Abilities** section for spell-like effects from equipment (e.g. Teleport from Helm, Haste from Boots)
14. **Equipment** — Organized by category:
    - **Weapons**: Name, enhancement, special abilities
    - **Worn Items**: All slotted items with effect summaries
    - **Ioun Stones**: List with effects (note if in Wayfinder)
    - **Special Items**: Custom/unique items with full descriptions
    - **Figurines / Companions**: If any
    - **Consumed / Given Away**: Historical record of used-up items
    - Link standard Pathfinder items to d20pfsrd.com: `[Item Name](https://www.d20pfsrd.com/...)`
    - Mark custom/homebrew items with `*(custom)*`
15. **Campaign-Specific Features** (if any) — Dedicated section for non-standard abilities granted by the campaign (blessings, boons, custom systems like eidolon evolutions). Subsection per feature with quick-reference tables and links to features.md for full descriptions.

### Formatting Rules

- **Traceability**: Every derived number shows its math. AC 16 = 10 + 2 DEX + 4 Mage Armor. Don't just state totals.
- **Links**: Every spell, feat, and feature name links to its detail in the corresponding reference file: `[Spell Name](spells.md#spell-name)`
- **Equipment links**: Standard Pathfinder items link to d20pfsrd.com. Custom/homebrew items are marked `*(custom)*`.
- **Always-on bonuses**: Bake permanent bonuses (luck, competence from always-active items/abilities) into totals. Don't relegate them to "situational" footnotes if they're always active.
- **Tactical reminders**: For key reactive items (Bracelet of Second Chances, reroll abilities, etc.), add a bold "Don't forget" callout near the stats they protect (AC, saves). These are easy to miss in combat.
- **Planned vs current**: Anything not available at current level: `*(planned)*`
- **Source attribution**: Feats show level taken. Spells show source (chosen, bloodline bonus, curse bonus, archetype, or item like "Page of Spell Knowledge"). Skills show what contributes to "other" bonuses.
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

## state.md Structure

The state file tracks live, session-to-session combat and exploration state. It persists between conversations so you can pick up mid-combat next session.

```markdown
# {Name} — Active State

*Last updated: 2026-03-26, round 3 of combat vs 2 vampires*

## Combat Toggles

Modifiers you routinely activate in combat. These are applied by default when generating attack/damage rolls.

| Toggle | Effect | Notes |
|--------|--------|-------|
| Deadly Aim | -4 attack / +8 damage | Always on for ranged |
| Rapid Shot | -2 attack / +1 extra attack | Full attack only |

## Active Buffs

| Buff | Source | Effect | Duration | Rounds Left |
|------|--------|--------|----------|-------------|
| Divine Favor | Self (spell) | +3 luck to attack & damage | 1 min | 7 |
| Shield of Faith | Self (spell) | +3 deflection AC | 13 min | — |
| Bit of Luck | Domain power | Next d20 rolls twice, takes better | 1 round | 1 |

## Active Conditions

| Condition | Source | Effect | Duration |
|-----------|--------|--------|----------|
| Shaken | Enemy fear aura | -2 attacks, saves, skill checks, ability checks | Until end of encounter |

## Ability Modifications

Temporary changes to ability scores (enhancement, drain, damage, penalties).

| Ability | Modifier | Type | Source | Duration |
|---------|----------|------|--------|----------|
| DEX | -2 | Drain | Vampire slam | Permanent until restored |
| WIS | +4 | Enhancement | Owl's Wisdom | 13 min |

## Resource Tracking

### Spells Remaining

| Level | Total | Used | Remaining |
|-------|-------|------|-----------|
| 1st | 7 | 2 | 5 |
| 2nd | 6 | 1 | 5 |
| 3rd | 6 | 3 | 3 |
| 4th | 5 | 0 | 5 |
| 5th | 2 | 0 | 2 |

### Class Resources

| Resource | Total | Used | Remaining |
|----------|-------|------|-----------|
| Grit | 8 | 1 | 7 |
| Bit of Luck | 11/day | 3 | 8 |
| Binding Ties | 11/day | 0 | 11 |
| Seize the Initiative | 11/day | 1 | 10 |
| Good Fortune | 1/day | 0 | 1 |
| Unity | 2/day | 0 | 2 |

## Session Notes

Free-form notes about the current situation for continuity.

- Round 3 of combat, 2 vampires remaining (one at ~half HP)
- Roland is 40ft from south wall, behind partial cover
- Ally (Nettle) is adjacent to vampire 1, flanking with summoned creature
```

### state.md Conventions

- **Combat toggles** are separate from buffs — they're player choices that stay on across combats, not timed effects.
- **Rounds left** uses numbers for in-combat tracking, "—" for long-duration buffs that won't expire mid-combat.
- **Ability modifications** stack by type per PF1e rules. Note the type (enhancement, morale, drain, damage, penalty) so stacking is correct.
- **Resource tracking** resets on "new day" — when the user says they rest, clear all used counts and remove expired buffs/conditions.
- **Session notes** are free-form context for picking up next session. Include tactical positioning, enemy status, anything relevant.
- When state.md doesn't exist, the character has no active modifiers (fresh state).

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
- Use the higher HD and better BAB
- **Saves**: Pick one class's full save progression — you cannot mix (e.g. Fort from one class, Ref from another). Note which class's saves are used and why (e.g. "Inquisitor saves for better Will")
- Class features stack (both classes' features apply)
- Spellcasting sections are separate per class
- Skills use the better skill ranks per level
