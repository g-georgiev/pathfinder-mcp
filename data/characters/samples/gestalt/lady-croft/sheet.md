---
name: Lady Lara Croft
level: 16
classes: Gunslinger (Pistolero) 16 / Bard (Archaeologist) 16 (gestalt)
race: Human
alignment: "true neutral"
deity: Pharasma
---

# Lady Lara Croft — Level 16 Human Pistolero // Archaeologist Bard (Gestalt)

**"Knowledge is a kind of theft. Every tomb I enter, every artifact I carry out, I am stealing history from the dark. Pharasma does not mind — she prefers the past to be seen."**

| | |
|---|---|
| **Race** | Human (Chelaxian) |
| **Classes** | Gunslinger (Pistolero) 16 // Bard (Archaeologist) 16 |
| **Alignment** | True Neutral |
| **Deity** | Pharasma — goddess of fate, birth, death, and history. Lara is not exactly pious, but she respects the Lady of Graves as a professional courtesy. |
| **Size** | Medium |
| **Age** | 31 |
| **Description** | Tall, wiry, athletic — the body of someone who climbs for a living. Long dark hair tied in a single severe braid that falls past her shoulder blades. Sun-darkened skin from years of Osirian expeditions. Sharp grey eyes that miss nothing. She wears practical adventuring leathers — fitted dark trousers, a sleeveless blouse, bracers, climbing harness, sturdy boots, ammunition bandoleer. Two pistols holstered at her hips, carried low and tied to the thigh for fast draw. Speaks with a crisp, precise Chelaxian accent. Unsmiling when working. Exactly as charming as she needs to be, no more. |

## Class Table

| Slot | Class | Archetype | Hit Die |
|------|-------|-----------|---------|
| A | Gunslinger 16 | Pistolero | d10 |
| B | Bard 16 | Archaeologist | d8 |

**Gestalt resolution**: d10 HD (Gunslinger), full BAB (Gunslinger), best of each save.

## Quick Nav

| Sheet Sections | Reference Files |
|---|---|
| [Ability Scores](#ability-scores) | [Spell Reference](spells.md) |
| [Combat Stats](#combat-stats) | [Class Features](features.md) |
| [Skills](#skills) | [Feats Reference](feats.md) |
| [Feats](#feats) | [Backstory](backstory.md) |
| [Character Traits](#character-traits) | |
| [Class Features](#class-features--quick-reference) | |
| [Racial Abilities](#racial-abilities) | |
| [Bard Spellcasting](#bard-spellcasting) | |
| [Equipment](#equipment) | |
| [Build Decisions](#build-decisions) | |

---

## Ability Scores

20 point buy. +2 racial to DEX. All 4 level-up bumps (4/8/12/16) to DEX.

| Ability | Base | Racial | Level | Item | Total | Mod | Notes |
|---------|------|--------|-------|------|-------|-----|-------|
| STR | 10 | — | — | — | **10** | **+0** | Dump — she fights with pistols, climbs with dexterity |
| DEX | 16 | +2 | +4 | +4 (Belt) | **26** | **+8** | Primary. Attack, damage, AC, Reflex, initiative, half her skills |
| CON | 12 | — | — | +4 (Belt) | **16** | **+3** | HP, Fort |
| INT | 13 | — | — | +6 (Headband) | **19** | **+4** | Skills, Knowledge rolls. NOTE: skill points/level computed from permanent INT 13 (+1) |
| WIS | 12 | — | — | +6 (Headband) | **18** | **+4** | Grit pool, Will, Perception |
| CHA | 13 | — | — | +6 (Headband) | **19** | **+4** | Bard casting, Archaeologist's Luck rounds |

---

## Combat Stats

### AC

| Component | Bonus | Type | Source |
|-----------|-------|------|--------|
| Base | 10 | — | — |
| DEX | +8 | — | Ability |
| Armor | +8 | Armor | [+4 Mithral Chain Shirt](https://www.d20pfsrd.com/equipment/armor/chain-shirt/) |
| Nimble | +4 | Dodge | [Nimble](features.md#nimble) (Gunslinger 14 → +4) |
| Deflection | +3 | Deflection | [Ring of Protection +3](https://www.d20pfsrd.com/magic-items/rings/ring-of-protection/) |
| Natural Armor | +3 | Natural | [Amulet of Natural Armor +3](https://www.d20pfsrd.com/magic-items/wondrous-items/a-b/amulet-of-natural-armor/) |
| Insight | +1 | Insight | [Dusty Rose Prism Ioun Stone](https://www.d20pfsrd.com/magic-items/wondrous-items/h-l/ioun-stones/dusty-rose-prism-ioun-stone/) |

| | Total |
|---|---|
| **AC** | **37** |
| **Touch** | **26** (10 + 8 DEX + 4 Nimble + 3 deflection + 1 insight) |
| **Flat-footed** | **25** (10 + 8 armor + 3 deflection + 3 natural + 1 insight; lose DEX and Nimble) |

With [Mirror Image](spells.md#mirror-image) (1d4+5 images, 16 min) layered on top, Lara is difficult to pin down even for creatures that can see through her stealth.

### HP

| Source | HP | Notes |
|--------|-----|-------|
| Hit Die (L1) | 10 | d10 max at 1st |
| Hit Dice (L2–16) | 90 | 15 × 6 (d10, half+1) |
| CON modifier | 48 | 16 × +3 |
| **Total HP** | **148** | |
| **Current wounds** | — | |

FCB (Human Bard): +1 bardic performance round/level (16 extra rounds) instead of HP. Total Archaeologist's Luck pool = 24 rounds base (4 + 4 CHA + 16 FCB), extended by [Lingering Performance](feats.md#lingering-performance).

### Saves

| Save | Base | Ability | Resistance | Total | Progression |
|------|------|---------|------------|-------|-------------|
| **Fort** | +10 | +3 (CON) | +5 (Cloak) | **+18** | Good (Gunslinger) |
| **Ref** | +10 | +8 (DEX) | +5 (Cloak) | **+23** | Good (both) |
| **Will** | +10 | +4 (WIS) | +5 (Cloak) | **+19** | Good (Bard) |

**Gestalt note**: Pistolero has good Fort, poor Ref, poor Will. Bard has poor Fort, good Ref, good Will. Gestalt takes the better of each → all three are good saves. Lara has fortress saves.

**Special saves:** [Uncanny Dodge](features.md#uncanny-dodge) — retains DEX bonus to AC even when flat-footed or struck by invisible attacker. [Evasion](features.md#evasion) — half damage from AoE on failed Ref save, *none* on success. [Trap Sense +5](features.md#trap-sense) — bonus to Reflex saves and AC against traps.

### Offense

| Stat | Value | Breakdown |
|------|-------|-----------|
| **BAB** | +16 | Gunslinger 16 (full BAB) |
| **Initiative** | **+12** | +8 DEX + 2 [Reactionary](#character-traits) + 2 [Gunslinger Initiative](features.md#gunslinger-initiative) (deed, passive with 1+ grit) |
| **Speed** | 30 ft. | Human base; 60 ft. with [Haste](spells.md#haste) |
| **CMB** | +16 | BAB +16 + STR 0 |
| **CMD** | **38** | 10 + 16 BAB + 0 STR + 8 DEX + 4 Nimble |
| **Concentration** | **+20** | CL 16 + CHA 4 |

### Attacks

**Weapons**: Twin **masterwork pistols** (+5 enhancement), carried in thigh holsters. Not named — Lara is a professional and treats them as tools. She owns backup pistols in her pack for when one misfires.

**Crit Range**: 20/×4 (pistol base — firearms have devastating crit multiplier)

#### Full Attack (Dual Wield + Haste + Rapid Shot)

**8 shots per round**. All firearm shots target **Touch AC within the first range increment** (20 ft for pistols), which is the entire mechanical point of a firearms build.

| Attack | AB | Damage | Notes |
|--------|-----|--------|-------|
| Main 1 | **+29** | 1d8 + 29 + 4d6 | Highest main-hand iterative |
| Main 2 | +24 | 1d8 + 29 + 4d6 | 2nd iterative |
| Main 3 | +19 | 1d8 + 29 + 4d6 | 3rd iterative |
| Off 1 | **+29** | 1d8 + 29 + 4d6 | Highest off-hand (pistol = light for TWF, same penalty as main) |
| Off 2 | +24 | 1d8 + 29 + 4d6 | 2nd off-hand iterative |
| Off 3 | +19 | 1d8 + 29 + 4d6 | 3rd off-hand iterative |
| Rapid Shot | **+29** | 1d8 + 29 + 4d6 | Extra main-hand attack at highest BAB |
| Haste | **+29** | 1d8 + 29 + 4d6 | Extra main-hand attack at highest BAB |

**AB breakdown (all attacks, same calc for main/off)**: +16 BAB + 8 DEX + 5 weapon + 1 PBS + 4 Luck (+3 Archaeologist's Luck + 1 Fate's Favored) + 2 morale ([Heroism](spells.md#heroism)) + 1 Haste - 2 TWF - 2 Rapid Shot - 4 Deadly Aim = **+29**

With TWF + light off-hand weapons (pistols count as light), both hands suffer the same -2 penalty and the off-hand's highest attack matches the main hand's highest.

**Damage breakdown (per shot)**: 1d8 (pistol) + 5 weapon + 8 DEX (from [Pistol Training](features.md#pistol-training)) + 3 ([Pistol Training](features.md#pistol-training) flat bonus at L13+) + 4 Luck (Archaeologist's Luck +3 + Fate's Favored +1) + 1 PBS + 8 Deadly Aim (-4 atk / +8 dmg at BAB 16) = **1d8 + 29** base damage per shot

Note: Heroism's +2 bonus is to *attack rolls*, saves, and skill checks — NOT damage. So it doesn't stack into the damage breakdown.

**Signature Deed bonus**: +4d6 (from [Up Close and Deadly](features.md#up-close-and-deadly) applied to every shot for free via [Signature Deed](feats.md#signature-deed))

**Per-shot average**: 4.5 (d8) + 29 + 14 (4d6 avg) = **47.5 damage per hit**

**Full attack DPR (all hits)**: 8 × 47.5 = **380 damage per round**

Firearms hit touch AC, so she lands on essentially every shot against anything short of CR-appropriate incorporeal creatures. The realistic hit rate against a CR 16 enemy (touch AC ~16-20) is >95% on every shot.

#### Critical Hits

Pistols crit on **20/×4**. That's a 5% threat rate with a 4× multiplier. On a confirmed crit:
- Weapon damage × 4 = 1d8 × 4 + 23 × 4 = ~110 weapon damage
- Up Close and Deadly spell damage × 2 (Spellstrike-style rule for extra dice on crit) = 8d6 avg 28

**Per-crit average**: ~138 damage on a single shot.

On an 8-shot round, ~40% chance one shot crits = ~+70 extra damage per round on average.

**Crit confirmation**: +28 attack bonus is almost automatic against touch AC.

#### Grit Pool

[Grit](features.md#grit): 4 base (WIS mod) + regenerate 1 per **killing blow or confirmed crit on 20**. Against anything that dies in 1-3 rounds, Lara's grit pool is effectively infinite.

[Signature Deed](feats.md#signature-deed) applied to Up Close and Deadly means she spends **zero grit** on her damage bonus. The remaining grit pool is available for:
- [Lightning Reload](features.md#lightning-reload) — 1 grit maintains always-active free reload capability
- [Gunslinger's Dodge](features.md#gunslingers-dodge) — spend 1 grit to negate an incoming attack
- [Dead Shot](features.md#dead-shot) — full-round alpha strike (makes one attack roll at highest BAB, adds damage from every iterative)
- [Gunslinger Initiative](features.md#gunslinger-initiative) — 1 grit, +4 initiative (already included in init breakdown above)

#### Reload Economy (The Fiddly Part)

Pistols hold 1 shot each. For a full attack with 8 shots, Lara needs to reload 6 times (starts the round with 2 loaded pistols). Handled as follows:

- [Rapid Reload](feats.md#rapid-reload-pistol) (free from Gunslinger class feature) + **alchemical cartridges** = **free-action reload** per shot
- [Lightning Reload](features.md#lightning-reload) deed at Gunslinger 11 = one free-action reload per round without requiring a free hand (covers the off-hand when both hands are busy)
- **Community interpretation**: During a full attack, the "free hand" requirement for reloading is satisfied transiently between shots — the hand that just fired becomes momentarily free while the other hand fires, allowing interleaved reload. This is the standard ruling at tables allowing dual-wield firearms builds.

Lara keeps 6 additional pre-loaded pistols in a bandolier as backup in case of misfire or dead-air (unfixable jam). Misfire rate on pistols is low (1 on a nat 1 attack roll) and [Quick Clear](features.md#quick-clear) handles standard misfires with a standard action.

#### Attack Modifiers Reference

| Modifier | AB | Damage | Source |
|----------|-----|--------|--------|
| Deadly Aim | -4 | +8 | [Feat](feats.md#deadly-aim) |
| Rapid Shot | -2 | — | [Feat](feats.md#rapid-shot) |
| Two-Weapon Fighting | -2 / -2 | — | [Feat chain](feats.md#two-weapon-fighting) |
| Haste | +1 | — | [Spell](spells.md#haste) |
| Archaeologist's Luck | +4 (+4 dmg) | +4 | [Feature](features.md#archaeologists-luck) (Fate's Favored +1) |
| Heroism | +2 morale | — | [Spell](spells.md#heroism) |
| Point-Blank Shot | +1 | +1 | [Feat](feats.md#point-blank-shot) (within 30 ft) |
| Up Close and Deadly | — | +4d6 | [Deed](features.md#up-close-and-deadly) (every shot, via Signature Deed) |

---

## Skills

128 real ranks (6 Bard + 1 INT 13 mod + 1 Human Skilled = 8/level × 16 levels) + 48 phantom ranks from [Headband of Mental Superiority +6](https://www.d20pfsrd.com/magic-items/wondrous-items/h-l/headband-of-mental-superiority/) across 3 chosen Knowledge skills.

Note: Archaeologist **does NOT get Versatile Performance** (replaced by Clever Explorer). All skills are purchased directly.

**Bardic Knowledge**: +8 to all Knowledge checks (half bard level). [Lore Master](features.md#lore-master): take 10 on any Knowledge she has ranks in; 3/day take 20 as a standard action. [Jack of All Trades](features.md#jack-of-all-trades): use any skill untrained; at level 16, **every skill is a class skill**.

| Skill | Total | Ranks | Ability | Class | Other | Other Source |
|-------|-------|-------|---------|-------|-------|--------------|
| K(History) | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Arcana) | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Religion) | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Planes) | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Dungeoneering) | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Geography)† | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Nobility)† | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Local)† | **+31** | 16 | +4 INT | +3 | +8 | Bardic Knowledge |
| K(Nature) | **+19** | 8 | +4 INT | — | +8 | Bardic Knowledge |
| Perception | **+23** | 16 | +4 WIS | +3 | +8 | [Clever Explorer](features.md#clever-explorer) (½ class level) |
| Disable Device | **+35** | 16 | +8 DEX | +3 | +8 | [Clever Explorer](features.md#clever-explorer) |
| Stealth | **+27** | 16 | +8 DEX | +3 | — | |
| Acrobatics | **+27** | 16 | +8 DEX | +3 | — | |
| Climb | **+11** | 8 | +0 STR | +3 | — | |
| Swim | **+11** | 8 | +0 STR | +3 | — | |
| Use Magic Device | **+23** | 16 | +4 CHA | +3 | — | |
| Spellcraft | **+23** | 16 | +4 INT | +3 | — | |
| Linguistics | **+12** | 5 | +4 INT | +3 | — | |
| Sleight of Hand | **+19** | 8 | +8 DEX | +3 | — | |
| Sense Motive | **+15** | 8 | +4 WIS | +3 | — | |
| Diplomacy | **+15** | 8 | +4 CHA | +3 | — | |

†Headband phantom ranks (16 each, treated as real ranks for all purposes after 24 hrs worn).

**Ranks spent**: 128/128 real + 48 phantom

**Languages**: Common (Taldane), Kelish (Qadiran — for Osirian expeditions), Ancient Osiriani, Draconic, Celestial, Infernal (Chelaxian upbringing), Thassilonian. Lara reads more dead languages than most sages.

---

## Feats

| Level | Source | Feat | Type | Effect | Notes |
|-------|--------|------|------|--------|-------|
| 1 (Gunslinger) | Class | [Gunsmithing](feats.md#gunsmithing) | General | Craft and maintain firearms | Free from Gunslinger |
| 1 (Gunslinger) | Class | [Rapid Reload (Pistol)](feats.md#rapid-reload-pistol) | Combat | Reduce reload by 1 step | Free from Gunslinger; combined with alchemical cartridges = free-action reload |
| 1 (Gunslinger) | Class | [Exotic Weapon Proficiency (Firearms)](feats.md#exotic-weapon-proficiency-firearms) | Combat | Wield firearms without penalty | Free from Gunslinger |
| 1 (human) | Bonus | [Point-Blank Shot](feats.md#point-blank-shot) | Combat | +1 atk/dmg within 30 ft | Prereq for Rapid Shot |
| 1 | Character | [Precise Shot](feats.md#precise-shot) | Combat | No -4 penalty shooting into melee | Essential for any ranged build |
| 3 | Character | [Two-Weapon Fighting](feats.md#two-weapon-fighting) | Combat | -2/-2 penalty instead of -4/-4 | Pistols count as light for TWF |
| 5 | Character | [Deadly Aim](feats.md#deadly-aim) | Combat | -4 atk / +8 dmg at BAB +16 | Big damage boost; firearms hit touch AC so attack loss is minimal |
| 7 | Character | [Rapid Shot](feats.md#rapid-shot) | Combat | Extra attack at -2 to all | +1 main-hand shot per full attack |
| 9 | Character | [Improved Two-Weapon Fighting](feats.md#improved-two-weapon-fighting) | Combat | 2nd off-hand attack at -5 | BAB +6 prereq |
| 11 | Character | [Lingering Performance](feats.md#lingering-performance) | General | Bardic performance lasts 2 extra rounds after stopping | Essential — Archaeologist's Luck has limited duration |
| 13 | Character | [Greater Two-Weapon Fighting](feats.md#greater-two-weapon-fighting) | Combat | 3rd off-hand attack at -10 | BAB +11 prereq; full TWF chain online |
| 15 | Character | [Signature Deed](feats.md#signature-deed) | Grit | One deed costs 0 grit permanently | **Applied to Up Close and Deadly** — every pistol shot gets +4d6 for free |

**Total feats**: 9 (8 character + 1 human bonus) + 3 Gunslinger free feats.

Note: Gunslinger has no regular bonus feat slots (unlike Fighter) — the 3 "free" feats at level 1 are class feature grants, not recurring bonus feats. The feat budget is tighter than the Shwarma Master's gestalt (which benefited from Fighter + Wizard bonus feat stacking).

---

## Character Traits

| Trait | Type | Effect |
|-------|------|--------|
| [Fate's Favored](features.md#fates-favored) | Faith (Pharasma) | +1 to all luck bonuses. **Archaeologist's Luck becomes +4 at level 16 instead of +3** |
| [Reactionary](features.md#reactionary) | Combat | +2 trait bonus to initiative |

**Initiative stack**: +8 DEX + 2 Reactionary + 2 [Gunslinger Initiative](features.md#gunslinger-initiative) (deed, passive with 1+ grit) = **+12 initiative**. With Quick Draw (from [Combat Trick](features.md#rogue-talents) rogue talent at L4), Lara also draws her pistol as part of her initiative check — she enters combat already aimed.

---

## Class Features — Quick Reference

### Pistolero Gunslinger

| Level | Feature | Effect |
|-------|---------|--------|
| 1 | [Grit](features.md#grit) | 4 points/day (WIS mod). Regenerates on crits/killing blows |
| 1 | [Deeds](features.md#deeds) | Access to Gunslinger deed list |
| 1 | [Up Close and Deadly](features.md#up-close-and-deadly) | 1 grit: +1d6 damage per 4 levels on a pistol shot. **+4d6 at L16**. Via [Signature Deed](feats.md#signature-deed) this is FREE on every shot |
| 1 | [Quick Clear](features.md#quick-clear) | Standard action: remove broken condition from misfired pistol |
| 1 | [Gunslinger's Dodge](features.md#gunslingers-dodge) | 1 grit, immediate: avoid an attack that would hit |
| 1 | [Gunslinger Initiative](features.md#gunslinger-initiative) | +2 initiative passively; with 1 grit, +4 and auto-natural-20 on initiative |
| 1 | [Pistol-Whip](features.md#pistol-whip) | 1 grit: melee attack with pistol, add firearm enhancement + weapon damage dice |
| 2 | [Nimble](features.md#nimble) | +1 dodge to AC per 4 levels in light/no armor. **+4 at L14** |
| 3 | [Pistol Training](features.md#pistol-training) | +1 damage per 4 levels with one-handed firearms (**+4 at L15**). Pistolero unique: also adds DEX mod to damage as bonus |
| 3 | [Pistolero's Deed](features.md#pistoleros-deed) | Additional pistol-specific deeds |
| 7 | [Dead Shot](features.md#dead-shot) | Full-round: make one attack at highest BAB, add damage from every iterative |
| 7 | [Targeting](features.md#targeting) | 1 grit full-round: called shot with status effect |
| 11 | [Bleeding Wound](features.md#bleeding-wound) | Free action, 1 grit: add bleed damage equal to DEX mod on hit |
| 11 | [Lightning Reload](features.md#lightning-reload) | 1 grit maintained: reload one firearm as a free action (no free hand needed) |
| 15 | [Menacing Shot](features.md#menacing-shot) | 1 grit: shaken condition on visible enemies in range |
| 15 | [Expert Loading](features.md#expert-loading) | Re-roll misfire checks |

### Archaeologist Bard

| Level | Feature | Effect |
|-------|---------|--------|
| 1 | [Bardic Knowledge](features.md#bardic-knowledge) | +½ class level to all Knowledge checks, untrained allowed |
| 1 | [Archaeologist's Luck](features.md#archaeologists-luck) | Swift to activate, free to maintain: +3 luck to attack, damage, saves, skills. **+4 with Fate's Favored** |
| 1 | [Cantrips](features.md#cantrips) | 6 cantrips known, unlimited casting |
| 2 | [Clever Explorer](features.md#clever-explorer) | +½ class level to Disable Device and Perception. Half time to disable devices. Disarm magical traps. **Replaces Versatile Performance** |
| 2 | [Uncanny Dodge](features.md#uncanny-dodge) | Cannot be caught flat-footed, retains DEX against invisible attackers. **Replaces Well-Versed** |
| 3 | [Trap Sense](features.md#trap-sense) | +1 Reflex and AC vs traps (+5 at L15) |
| 4 | [Rogue Talent](features.md#rogue-talent) | Selection: **Combat Trick** — bonus feat |
| 5 | [Lore Master](features.md#lore-master) | Take 10 on any Knowledge check. 1/day (+1 per 6 levels) take 20 as standard. **3/day at L17**, close at L16 |
| 6 | [Evasion](features.md#evasion) | Half damage on failed Ref save vs AoE, **none** on success |
| 8 | [Rogue Talent](features.md#rogue-talent) | **Ledge Walker** — move along narrow surfaces at full speed |
| 10 | [Jack of All Trades](features.md#jack-of-all-trades) | Use any skill untrained. **At level 16, every skill is a class skill** |
| 12 | [Rogue Talent](features.md#rogue-talent) | **Finesse Rogue** — free Weapon Finesse |
| 16 | [Rogue Talent](features.md#rogue-talent) | **Dispelling Attack** (advanced) — sneak attacks act as targeted dispel magic |

### Resource Summary

| Resource | Uses/Day | Notes |
|----------|----------|-------|
| [Archaeologist's Luck](features.md#archaeologists-luck) | 24 rounds base | 4 + CHA mod + Human FCB (16) = 24. With Lingering Performance, ~34-40 effective rounds |
| [Grit](features.md#grit) | 4 pool | Regens on crits and killing blows. Effectively infinite in combat |
| [Lore Master](features.md#lore-master) take 20 | 3/day | Standard action |
| [Gunslinger's Dodge](features.md#gunslingers-dodge) | Pool | Immediate action reaction |
| Bardic Spells | See below | CHA-based |

---

## Racial Abilities

| Trait | Effect |
|-------|--------|
| [Ability Score Modifier](features.md#ability-score-modifier) | +2 to one ability score (DEX) |
| [Bonus Feat](features.md#bonus-feat) | Extra feat at 1st level ([Point-Blank Shot](feats.md#point-blank-shot)) |
| [Skilled](features.md#skilled) | +1 skill rank per level (+16 total) |
| [Languages](features.md#languages) | Common + bonus languages from INT |

**Favored Class Bonus**: Human Bard FCB adds +1 round of bardic performance per level. Over 16 levels: **+16 bonus rounds** of [Archaeologist's Luck](features.md#archaeologists-luck) per day.

---

## Bard Spellcasting

**Caster Level**: 16
**Casting Stat**: CHA
**Base Save DC**: 10 + spell level + 4 (CHA) = **14 + spell level**
**Concentration**: **+20** (CL 16 + CHA 4)
**Casting type**: Spontaneous (bard doesn't prepare spells; knows N and can cast any of them)

### Spells Known (all from Bard spell list, max 6th level)

| Level | Known |
|-------|-------|
| 0 (cantrips) | 6 |
| 1st | 6 |
| 2nd | 6 |
| 3rd | 5 |
| 4th | 5 |
| 5th | 4 |
| 6th | 4 |

### Slots Per Day

| Level | Base | CHA Bonus | Total |
|-------|------|-----------|-------|
| 0 (cantrips) | 4 | — | **4** (at will) |
| 1st | 5 | +1 | **6** |
| 2nd | 5 | +1 | **6** |
| 3rd | 5 | +1 | **6** |
| 4th | 5 | +1 | **6** |
| 5th | 5 | — | **5** |
| 6th | 3 | — | **3** |
| **Total** | | | **32** + cantrips |

### Cantrips (at will)

| Spell | Action | Effect |
|-------|--------|--------|
| [Detect Magic](spells.md#detect-magic) | 1 std | Detect magical auras in 60 ft cone |
| [Read Magic](spells.md#read-magic) | 1 std | Read arcane scrolls and spellbooks (essential for a treasure hunter) |
| [Prestidigitation](spells.md#prestidigitation) | 1 std | Minor utility magic |
| [Mage Hand](spells.md#mage-hand) | 1 std | Telekinesis, 5 lb. Retrieve keys, trigger distant switches |
| [Ghost Sound](spells.md#ghost-sound) | 1 std | Create sound. Distraction, misdirection |
| [Light](spells.md#light) | 1 std | Torch-level light on object, 16 hours |

### 1st-Level Spells (6/day)

| Spell | Action | Duration | Effect |
|-------|--------|----------|--------|
| [Comprehend Languages](spells.md#comprehend-languages) | 1 std | 16 min | Understand any language — essential for reading ruins |
| [Grease](spells.md#grease) | 1 std | 16 min | 10-ft square, Ref or fall; **DC 15** |
| [Hideous Laughter](spells.md#hideous-laughter) | 1 std | 16 rd | Target prone and helpless; **DC 15** |
| [Cure Light Wounds](spells.md#cure-light-wounds) | 1 std | Instantaneous | 1d8 + 16 healing |
| [Identify](spells.md#identify) | 1 std | Instantaneous | +10 to Spellcraft for magic item ID |
| [Saving Finale](spells.md#saving-finale) | 1 imm | Instantaneous | Immediate reroll on failed save |

### 2nd-Level Spells (6/day)

| Spell | Action | Duration | Effect |
|-------|--------|----------|--------|
| [Glitterdust](spells.md#glitterdust) | 1 std | 16 rd | Blind + outline invisible; **DC 16** Will neg blind |
| [Heroism](spells.md#heroism) | 1 std | 160 min | +2 morale to attacks, saves, skills |
| [Mirror Image](spells.md#mirror-image) | 1 std | 16 min | 1d4+5 decoy images (max 8) |
| [Invisibility](spells.md#invisibility) | 1 std | 16 min | Invisible until attacking |
| [Tongues](spells.md#tongues) | 1 std | 160 min | Speak and understand any language |
| [Detect Thoughts](spells.md#detect-thoughts) | 1 std | 16 min | Read surface thoughts; **DC 16** Will neg |

### 3rd-Level Spells (5/day)

| Spell | Action | Duration | Effect |
|-------|--------|----------|--------|
| [Haste](spells.md#haste) | 1 std | 16 rd | +1 atk/AC/Ref, +30 speed, extra attack for 16 creatures |
| [Good Hope](spells.md#good-hope) | 1 std | 16 rd | +2 morale atk/dmg/saves/checks, party-wide |
| [Dispel Magic](spells.md#dispel-magic) | 1 std | Instantaneous | d20+10 vs DC 11+CL |
| [Fly](spells.md#fly) | 1 std | 16 min | 60 ft fly speed (good) |
| [Displacement](spells.md#displacement) | 1 std | 16 rd | 50% miss chance vs attacks |

### 4th-Level Spells (5/day)

| Spell | Action | Duration | Effect |
|-------|--------|----------|--------|
| [Dimension Door](spells.md#dimension-door) | 1 std | Instantaneous | Teleport up to 1,080 ft. |
| [Freedom of Movement](spells.md#freedom-of-movement) | 1 std | 160 min | Immune to grapple, paralysis, impediments |
| [Greater Invisibility](spells.md#greater-invisibility) | 1 std | 16 rd | Invisible even while attacking |
| [Break Enchantment](spells.md#break-enchantment) | 1 min | Instantaneous | Remove curses, charms, transformations |
| [Hold Monster](spells.md#hold-monster) | 1 std | 16 rd | Paralyze creature; **DC 18** Will neg |

### 5th-Level Spells (4/day)

| Spell | Action | Duration | Effect |
|-------|--------|----------|--------|
| [Greater Heroism](spells.md#greater-heroism) | 1 std | 16 min | +4 morale atk/saves/skills + 16 temp HP + fear immunity |
| [Greater Dispel Magic](spells.md#greater-dispel-magic) | 1 std | Instantaneous | d20+16 vs DC 11+CL, area dispel option |
| [Song of Discord](spells.md#song-of-discord) | 1 std | 16 rd | Enemies attack each other; **DC 19** Will neg |
| [Cure Critical Wounds](spells.md#cure-critical-wounds) | 1 std | Instantaneous | 4d8 + 16 healing |

### 6th-Level Spells (3/day)

| Spell | Action | Duration | Effect |
|-------|--------|----------|--------|
| [True Seeing](spells.md#true-seeing) | 1 std | 16 min | See through illusions, invisibility, transformations, alignment |
| [Mass Suggestion](spells.md#mass-suggestion) | 1 std | 16 hr | Compel course of action on multiple targets; **DC 20** Will neg |
| [Heroes' Feast](spells.md#heroes-feast) | 10 min | Instantaneous | Party-wide buff: +1 attack/Will, +1d8+4 temp HP, fear immunity, poison/disease cure |
| [Analyze Dweomer](spells.md#analyze-dweomer) | 1 std | 16 rd | Identify every magical effect on creatures and objects in range |

---

## Equipment

### Weapons

| Item | Cost | Enhancement | Notes |
|------|------|-------------|-------|
| +5 Pistol (primary) | 50,315 gp | +5 enhancement | Holstered low on right thigh, tied down |
| +5 Pistol (secondary) | 50,315 gp | +5 enhancement | Holstered low on left thigh |
| Masterwork pistol × 6 | 1,800 gp (300 each) | Backup | Bandolier across chest. Loaded in advance with alchemical cartridges for use if primaries misfire |
| Alchemical cartridges (paper) × 200 | 2,400 gp | Ammunition | Free-action reload combined with Rapid Reload |
| Alchemical cartridges (dragon's breath) × 20 | 700 gp | Special ammo | Cone attack; flavor for dramatic moments |

### Worn Items

| Slot | Item | Effect | Cost |
|------|------|--------|------|
| Body | [+4 Mithral Chain Shirt](https://www.d20pfsrd.com/equipment/armor/chain-shirt/) | Light armor, +8 AC, no ASF, no speed reduction | 17,100 |
| Head | [Headband of Mental Superiority +6](https://www.d20pfsrd.com/magic-items/wondrous-items/h-l/headband-of-mental-superiority/) | +6 INT, WIS, CHA. 16 ranks each in K(Geography), K(Nobility), K(Local) | 144,000 |
| Belt | [Belt of Physical Might +4 (DEX/CON)](https://www.d20pfsrd.com/magic-items/wondrous-items/a-b/belt-of-physical-might/) | +4 DEX, +4 CON | 40,000 |
| Shoulders | [Cloak of Resistance +5](https://www.d20pfsrd.com/magic-items/wondrous-items/c-d/cloak-of-resistance/) | +5 resistance to all saves | 25,000 |
| Ring 1 | [Ring of Protection +3](https://www.d20pfsrd.com/magic-items/rings/ring-of-protection/) | +3 deflection AC | 18,000 |
| Neck | [Amulet of Natural Armor +3](https://www.d20pfsrd.com/magic-items/wondrous-items/a-b/amulet-of-natural-armor/) | +3 natural armor enhancement | 18,000 |
| Ioun | [Dusty Rose Prism Ioun Stone](https://www.d20pfsrd.com/magic-items/wondrous-items/h-l/ioun-stones/dusty-rose-prism-ioun-stone/) | +1 insight AC | 5,000 |
| Feet | [Boots of Striding and Springing](https://www.d20pfsrd.com/magic-items/wondrous-items/a-b/boots-of-striding-and-springing/) | +10 ft speed, +5 Acrobatics (jumps) | 5,500 |
| Back | [Handy Haversack](https://www.d20pfsrd.com/magic-items/wondrous-items/h-l/handy-haversack/) | Extradimensional storage | 2,000 |

### Adventurer's Kit

| Item | Cost | Notes |
|------|------|-------|
| Masterwork thieves' tools | 100 | +2 Disable Device |
| [Traveler's Any-Tool](https://www.d20pfsrd.com/magic-items/wondrous-items/r-z/traveler-s-any-tool/) | 250 | Transforms into any mundane tool; +2 Craft/Profession |
| Silk rope (100 ft.) × 2 | 40 | Climbing |
| Grappling hook | 1 | Paired with rope |
| Climber's kit | 80 | +2 Climb |
| Flint & steel | 1 | |
| Sunrods × 10 | 20 | Dark ruins |
| Waterskin | 1 | |
| Trail rations × 10 | 5 | |
| Blanket | 0.5 | |
| Journal & ink | 12 | Field notes on discoveries |
| Spyglass | 1,000 | Surveying ruins from a distance |
| Magnifying glass | 100 | Examining artifacts |
| Compass | 10 | Wayfinding |
| Bag of caltrops | 1 | Pursuit deterrent |
| Tindertwigs × 20 | 20 | Reliable ignition |

### Scrolls & Consumables

| Item | Effect | Cost |
|------|--------|------|
| Wand of [Cure Light Wounds](spells.md#cure-light-wounds) (50 charges) | Between-combat healing, UMD backup | 750 |
| Scroll of [Teleport](spells.md#teleport) × 3 | Emergency exit (Teleport isn't on bard list — UMD required) | 3,375 |
| Scroll of [Stone Shape](spells.md#stone-shape) × 5 | Open sealed passages (UMD) | 1,875 |
| Scroll of [Comprehend Languages](spells.md#comprehend-languages) × 10 | Backup for reading inscriptions | 250 |
| Potion of Fly × 3 | Emergency flight | 2,250 |
| Alchemist's fire × 10 | Backup thrown weapon | 200 |
| Holy water × 5 | Anti-undead emergency | 125 |

### Wealth Summary

| Category | Cost |
|----------|------|
| Weapons & ammo | 105,530 |
| Worn items | 274,600 |
| Kit & consumables | 9,531 |
| **Total spent** | **~389,661** |
| **WBL (level 16)** | 315,000 |
| **Notes** | Slightly over WBL due to the combined cost of Mental Superiority +6 and dual +5 pistols. At a strict-WBL table, drop pistols to +4 and save 36,000 gp |

---

## Build Decisions

### Why This Gestalt Works — The Action Economy

Gunslinger and Archaeologist Bard stack cleanly because **every Bard feature is passive or uses the swift slot differently from Gunslinger deeds**:

| Class | Contribution | Action Cost |
|-------|-------------|-------------|
| Gunslinger (Pistolero) | Full BAB, pistol full attacks, grit deeds, Up Close and Deadly damage, Nimble AC, Pistol Training (DEX to damage), Lightning Reload | Round 1 swift: reserved. Round 2+ swift: Gunslinger's Dodge reaction OR Menacing Shot OR other deeds. **Signature Deed makes Up Close and Deadly free, so the swift is genuinely open after round 1** |
| Bard (Archaeologist) | Full 6th-level casting, Archaeologist's Luck (+4 to everything), Evasion, Uncanny Dodge, Trap Sense, skill density, Rogue Talents, Lore Master | Round 1 swift: activate Luck (then maintained as free action). All other features passive or pre-cast |

Both classes run simultaneously. The Bard's spell slots cast Haste/Heroism/Greater Invisibility pre-combat or on round 1, then Lara full-attacks every subsequent round with all the stacked buffs active.

### What Lara's Turn Looks Like

**Round 1** (surprise or combat start):
- Free: Grit for Gunslinger Initiative (+4 init) → she always goes first
- Swift: Activate [Archaeologist's Luck](features.md#archaeologists-luck) (+4 luck to everything, lasts whole fight as free maintenance)
- Move: Position, draw pistols if not already drawn (Quick Draw not needed — Gunslingers always have firearms ready by convention)
- Standard: Fire one pistol as a single attack OR cast a spell ([Haste](spells.md#haste), [Heroism](spells.md#heroism), [Mirror Image](spells.md#mirror-image))

**Round 2+** (full attack routine):
- Swift: Free (Signature Deed makes Up Close and Deadly automatic). Optionally spend grit on a deed.
- Free: Maintain Luck, reload pistols between shots
- Full attack: **8 shots** with Haste + Rapid Shot + Greater TWF, each dealing 1d8 + 23 + 4d6 (~41.5 damage), targeting touch AC

**DPR**: ~380 average, ~450+ with crits. Against a solar (CR 23, touch AC 14): 8/8 shots land, ~380 damage per round.

**Nova round** (boss fight):
- Swift: still free
- Full: [Dead Shot](features.md#dead-shot) deed (full round, 1 grit) — make one attack roll at highest BAB, add damage from every iterative attack. Total damage: ~330 in ONE shot, which bypasses DR much better than 8 separate shots.

### Why Pistolero Over Mysterious Stranger

**Researched and confirmed**: Pistolero and Mysterious Stranger **cannot stack** (both modify Gun Training 1 — confirmed via `check_archetype_compatibility` MCP tool). Had to pick one.

**Pistolero wins** for damage output:
- **Up Close and Deadly** (+4d6 per shot) vs Mysterious Stranger's **Focused Aim** (+CHA mod per shot = +4). With Signature Deed applied, Up Close and Deadly delivers 14 avg per shot vs Focused Aim's 4. Over 8 shots that's **+80 extra damage per round** (and +10d6 vs +2d8 on crits).
- **Pistol Training** adds DEX to damage with pistols at Gunslinger 5 (not just Gun Training). Mysterious Stranger gets vanilla Gun Training.
- **Pistol-specific deeds** (Dead Shot, Twin Shot Knock) vs Mysterious Stranger's general lucky shots.

**Cost**: WIS 12 for grit pool (+1 baseline from mod, +6 from headband = 4 grit). Lara is not a CHA-SAD build, but she doesn't need to be — with Human Bard FCB adding 16 bardic rounds per day, her CHA doesn't need to be maxed.

### Why Human

- **Bonus feat** — this build is feat-starved (9 feats total vs Shwarma Master's 15)
- **Favored Class Bonus**: +1 bardic performance round per level. Over 16 levels, that's **16 extra rounds of Archaeologist's Luck per day** — enough to cover 4-5 full combats without running dry
- **Skilled**: +1 skill rank per level (+16 total)
- **Chelaxian flavor** fits the "British aristocrat" reskin perfectly — noble house, inherited wealth, turned her back on Cheliax's politics to pursue archaeology

### Why Pharasma

Pharasma is the goddess of **fate, birth, death, and history**. She is the Lady of Graves. Every tomb Lara enters is technically Pharasma's domain, and every artifact she recovers is a piece of history Pharasma has been quietly waiting for someone to uncover. Lara is not devout — she considers herself a practical rationalist — but she leaves a coin at every shrine to Pharasma she passes, and she has never had a Phasmic dream that told her to turn back from a ruin. She considers their relationship professional.

Also, **Fate's Favored trait** (which boosts Archaeologist's Luck to +4) is a Faith trait tied to Pharasma. Mechanical alignment is clean.

### Why Dual Pistols (The Flavor Call)

**Flavor won over optimization.** A single-pistol or single-musket Gunslinger would deal nearly as much DPR with far cleaner action economy and half the feat cost. But Lara Croft carries *two pistols*. That's non-negotiable.

Consequences:
- **3 feats on the TWF chain** (TWF, ITWF, GTWF) that a single-pistol build wouldn't need
- **Reload management** is genuinely fiddly — see the Reload Economy section above
- **Backup pistols in a bandolier** for misfire contingencies
- **Alchemical cartridges mandatory** to achieve free-action reload

Upsides:
- **8 shots per round** via TWF + Rapid Shot + Haste vs ~4-5 with a single pistol
- Covers both "rapid trigger spam" and "alpha strike via Dead Shot" playstyles
- Looks cool

### Why No Pistol Names

Canonical research: across all Tomb Raider media (1996-present, games/films/comics), Lara has **never named her twin pistols**. She refers to them as "pistols" or "guns" or by model designation only. She is a rationalist who treats tools as tools. When a pistol breaks, she replaces it with another pistol. When she needs six backups for misfire scenarios, she carries six backups. The pistols are not friends. They are *equipment*. This is one of the defining character traits that separates Lara from the "my sword is my soul" adventurer archetype, and the build preserves it.

### Sources & Guides Consulted

**MCP Database**: All spells, feats, features, archetypes, items, and classes looked up via `pathfinder-data` MCP tools with `expand=True`. Archetype compatibility verified via `check_archetype_compatibility(base_class='gunslinger', archetype_names=['Pistolero', 'Mysterious Stranger'])` which returned `compatible: false` due to shared modification of Gun Training 1.

**Guides searched** (via `search_guides`):

| Guide | What It Contributed |
|-------|---------------------|
| [gestalt-guide](../../guides/gestalt-guide/) | Bard // Fighter rated 4 stars; general Bard gestalt advice; Archaeologist-specific notes |
| [bard-buffer](../../guides/bard-buffer/) | Archaeologist self-buff philosophy; Lingering Performance rationale |
| [gunslinger-lokotor](../../guides/gunslinger-lokotor/) | Pistolero dual-wield build principles; Signature Deed priority |
| [gunslinger-njolly](../../guides/gunslinger-njolly/) | Grit management; deed priority lists |

**Web research**: Paizo forums on Archaeologist Bard self-buff builds, dual-pistol Gunslinger action economy, Signature Deed interactions with Up Close and Deadly, community consensus on dual-wield firearm reload interpretation. Lara Croft canon pistol names verified (none exist).
