"""Spell slot computation for Pathfinder 1e characters.

Handles spells_per_day lookup from class data, bonus spells from ability
scores, and hardcoded fallback tables for classes with broken DB data.
"""

# Fallback spells-per-day tables for classes whose DB data is incomplete.
# Format: spells_per_day[class_level - 1][spell_level] = base slots (or None)
# These match the official Pathfinder 1e Core Rulebook tables.

FALLBACK_SPELL_TABLES = {
    "cleric": {
        "casting_ability": "WIS",
        "type": "divine",
        "spontaneous": False,
        "spells_per_day": [
            # L1-20: [0th, 1st, 2nd, 3rd, 4th, 5th, 6th, 7th, 8th, 9th]
            [3, 1+1, None, None, None, None, None, None, None, None],
            [4, 2+1, None, None, None, None, None, None, None, None],
            [4, 2+1, 1+1, None, None, None, None, None, None, None],
            [4, 3+1, 2+1, None, None, None, None, None, None, None],
            [4, 3+1, 2+1, 1+1, None, None, None, None, None, None],
            [4, 3+1, 3+1, 2+1, None, None, None, None, None, None],
            [4, 4+1, 3+1, 2+1, 1+1, None, None, None, None, None],
            [4, 4+1, 3+1, 3+1, 2+1, None, None, None, None, None],
            [4, 4+1, 4+1, 3+1, 2+1, 1+1, None, None, None, None],
            [4, 4+1, 4+1, 3+1, 3+1, 2+1, None, None, None, None],
            [4, 4+1, 4+1, 4+1, 3+1, 2+1, 1+1, None, None, None],
            [4, 4+1, 4+1, 4+1, 3+1, 3+1, 2+1, None, None, None],
            [4, 4+1, 4+1, 4+1, 4+1, 3+1, 2+1, 1+1, None, None],
            [4, 4+1, 4+1, 4+1, 4+1, 3+1, 3+1, 2+1, None, None],
            [4, 4+1, 4+1, 4+1, 4+1, 4+1, 3+1, 2+1, 1+1, None],
            [4, 4+1, 4+1, 4+1, 4+1, 4+1, 3+1, 3+1, 2+1, None],
            [4, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1, 3+1, 2+1, 1+1],
            [4, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1, 3+1, 3+1, 2+1],
            [4, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1, 3+1, 3+1],
            [4, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1, 4+1],
        ],
    },
    "druid": {
        "casting_ability": "WIS",
        "type": "divine",
        "spontaneous": False,
        "spells_per_day": [
            [3, 1, None, None, None, None, None, None, None, None],
            [4, 2, None, None, None, None, None, None, None, None],
            [4, 2, 1, None, None, None, None, None, None, None],
            [4, 3, 2, None, None, None, None, None, None, None],
            [4, 3, 2, 1, None, None, None, None, None, None],
            [4, 3, 3, 2, None, None, None, None, None, None],
            [4, 4, 3, 2, 1, None, None, None, None, None],
            [4, 4, 3, 3, 2, None, None, None, None, None],
            [4, 4, 4, 3, 2, 1, None, None, None, None],
            [4, 4, 4, 3, 3, 2, None, None, None, None],
            [4, 4, 4, 4, 3, 2, 1, None, None, None],
            [4, 4, 4, 4, 3, 3, 2, None, None, None],
            [4, 4, 4, 4, 4, 3, 2, 1, None, None],
            [4, 4, 4, 4, 4, 3, 3, 2, None, None],
            [4, 4, 4, 4, 4, 4, 3, 2, 1, None],
            [4, 4, 4, 4, 4, 4, 3, 3, 2, None],
            [4, 4, 4, 4, 4, 4, 4, 3, 2, 1],
            [4, 4, 4, 4, 4, 4, 4, 3, 3, 2],
            [4, 4, 4, 4, 4, 4, 4, 4, 3, 3],
            [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        ],
    },
    "paladin": {
        "casting_ability": "CHA",
        "type": "divine",
        "spontaneous": False,
        "spells_per_day": [
            # Paladins don't cast until level 4
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, 0, None, None, None],
            [None, 1, None, None, None],
            [None, 1, None, None, None],
            [None, 1, 0, None, None],
            [None, 1, 1, None, None],
            [None, 2, 1, None, None],
            [None, 2, 1, 0, None],
            [None, 2, 1, 1, None],
            [None, 2, 2, 1, None],
            [None, 3, 2, 1, 0],
            [None, 3, 2, 1, 1],
            [None, 3, 2, 2, 1],
            [None, 3, 3, 2, 1],
            [None, 4, 3, 2, 1],
            [None, 4, 3, 2, 2],
            [None, 4, 3, 3, 2],
            [None, 4, 4, 3, 3],
        ],
    },
    "ranger": {
        "casting_ability": "WIS",
        "type": "divine",
        "spontaneous": False,
        "spells_per_day": [
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, 0, None, None, None],
            [None, 1, None, None, None],
            [None, 1, None, None, None],
            [None, 1, 0, None, None],
            [None, 1, 1, None, None],
            [None, 2, 1, None, None],
            [None, 2, 1, 0, None],
            [None, 2, 1, 1, None],
            [None, 2, 2, 1, None],
            [None, 3, 2, 1, 0],
            [None, 3, 2, 1, 1],
            [None, 3, 2, 2, 1],
            [None, 3, 3, 2, 1],
            [None, 4, 3, 2, 1],
            [None, 4, 3, 2, 2],
            [None, 4, 3, 3, 2],
            [None, 4, 4, 3, 3],
        ],
    },
    "bard": {
        "casting_ability": "CHA",
        "type": "arcane",
        "spontaneous": True,
        "spells_per_day": [
            [None, 1, None, None, None, None, None],
            [None, 2, None, None, None, None, None],
            [None, 3, None, None, None, None, None],
            [None, 3, 1, None, None, None, None],
            [None, 4, 2, None, None, None, None],
            [None, 4, 3, None, None, None, None],
            [None, 4, 3, 1, None, None, None],
            [None, 4, 4, 2, None, None, None],
            [None, 5, 4, 3, None, None, None],
            [None, 5, 4, 3, 1, None, None],
            [None, 5, 4, 4, 2, None, None],
            [None, 5, 5, 4, 3, None, None],
            [None, 5, 5, 4, 3, 1, None],
            [None, 5, 5, 4, 4, 2, None],
            [None, 5, 5, 5, 4, 3, None],
            [None, 5, 5, 5, 4, 3, 1],
            [None, 5, 5, 5, 4, 4, 2],
            [None, 5, 5, 5, 5, 4, 3],
            [None, 5, 5, 5, 5, 5, 4],
            [None, 5, 5, 5, 5, 5, 5],
        ],
    },
    "sorcerer": {
        "casting_ability": "CHA",
        "type": "arcane",
        "spontaneous": True,
        "spells_per_day": [
            [None, 3, None, None, None, None, None, None, None, None],
            [None, 4, None, None, None, None, None, None, None, None],
            [None, 5, None, None, None, None, None, None, None, None],
            [None, 6, 3, None, None, None, None, None, None, None],
            [None, 6, 4, None, None, None, None, None, None, None],
            [None, 6, 5, 3, None, None, None, None, None, None],
            [None, 6, 6, 4, None, None, None, None, None, None],
            [None, 6, 6, 5, 3, None, None, None, None, None],
            [None, 6, 6, 6, 4, None, None, None, None, None],
            [None, 6, 6, 6, 5, 3, None, None, None, None],
            [None, 6, 6, 6, 6, 4, None, None, None, None],
            [None, 6, 6, 6, 6, 5, 3, None, None, None],
            [None, 6, 6, 6, 6, 6, 4, None, None, None],
            [None, 6, 6, 6, 6, 6, 5, 3, None, None],
            [None, 6, 6, 6, 6, 6, 6, 4, None, None],
            [None, 6, 6, 6, 6, 6, 6, 5, 3, None],
            [None, 6, 6, 6, 6, 6, 6, 6, 4, None],
            [None, 6, 6, 6, 6, 6, 6, 6, 5, 3],
            [None, 6, 6, 6, 6, 6, 6, 6, 6, 4],
            [None, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        ],
    },
}


def _is_broken_spells_per_day(spells_per_day: list, level: int) -> bool:
    """Check if spells_per_day data is broken (all None except cantrips).

    A class at sufficient level should have non-None spell slots.
    If only index 0 is non-None for a full caster at level >= 2, data is broken.
    """
    if not spells_per_day or level < 1:
        return True
    if level > len(spells_per_day):
        return True
    row = spells_per_day[level - 1]
    if not row:
        return True
    # If every entry after cantrips (index 0) is None, data is broken
    non_cantrip = row[1:] if len(row) > 1 else []
    return all(v is None for v in non_cantrip)


def _bonus_spells(ability_mod: int, spell_level: int) -> int:
    """Compute bonus spell slots for a given spell level from ability modifier.

    Bonus spells for spell level S (S > 0) = 1 + (mod - S) // 4, if mod >= S.
    No bonus spells for cantrips (spell level 0).

    Args:
        ability_mod: The casting ability modifier.
        spell_level: The spell level (0-9).

    Returns:
        Number of bonus spell slots.
    """
    if spell_level <= 0:
        return 0
    if ability_mod < spell_level:
        return 0
    return 1 + (ability_mod - spell_level) // 4


def compute_spell_slots(
    classes: list[dict],
    class_data: dict,
    ability_mods: dict,
) -> dict:
    """Compute available spell slots per class per spell level.

    For each casting class, reads spells_per_day from class data (or
    fallback tables if data is broken). Adds bonus spells from the casting
    ability modifier for spell levels 1+.

    Args:
        classes: List of class dicts with "name" and "level".
        class_data: Dict keyed by lowercase class name -> parsed class data.
        ability_mods: Dict of ability modifiers.

    Returns:
        Dict keyed by class name -> {spell_level_str: total_slots}.
        e.g. {"wizard": {"0": 4, "1": 5, "2": 5, ...}}
    """
    result = {}

    for cls in classes:
        cls_name = cls.get("name", "").lower()
        cls_level = cls.get("level", 1)
        cd = class_data.get(cls_name, {})
        spellcasting = cd.get("spellcasting", {})

        if not spellcasting:
            # Check fallback tables
            if cls_name in FALLBACK_SPELL_TABLES:
                spellcasting = FALLBACK_SPELL_TABLES[cls_name]
            else:
                continue  # Non-casting class

        spells_per_day = spellcasting.get("spells_per_day", [])
        casting_ability = spellcasting.get("casting_ability", "INT").lower()
        ability_mod = ability_mods.get(casting_ability, 0)

        # Check if DB data is broken, use fallback if available
        if _is_broken_spells_per_day(spells_per_day, cls_level):
            fallback = FALLBACK_SPELL_TABLES.get(cls_name)
            if fallback:
                spells_per_day = fallback["spells_per_day"]
                casting_ability = fallback["casting_ability"].lower()
                ability_mod = ability_mods.get(casting_ability, 0)
            else:
                continue

        if cls_level < 1 or cls_level > len(spells_per_day):
            continue

        row = spells_per_day[cls_level - 1]
        if not row:
            continue

        slots = {}
        for spell_level, base in enumerate(row):
            if base is None:
                continue
            bonus = _bonus_spells(ability_mod, spell_level)
            slots[str(spell_level)] = base + bonus

        if slots:
            result[cls_name] = slots

    return result
