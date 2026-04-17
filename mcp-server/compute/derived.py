"""Main orchestrator for derived stat computation.

Imports all compute sub-modules and assembles the full computed stats dict
for a character.
"""

from compute.progression import lookup_class_data
from compute.hp import compute_hp
from compute.saves import compute_saves
from compute.combat_stats import (
    compute_bab,
    compute_ac,
    compute_cmb_cmd,
    compute_initiative,
    compute_attack_lines,
)
from compute.skills import compute_skill_totals
from compute.spells import compute_spell_slots


def compute_derived_stats(character_data: dict, rules_db_path: str = None) -> dict:
    """Compute all derived statistics for a character.

    Looks up class data from the rules DB, then calls each compute function
    to build the full stat block: HP, saves, BAB, AC, CMB/CMD, initiative,
    attack lines, skill totals, and spell slots.

    Args:
        character_data: The character's data dict (abilities, classes,
            feats, equipment, skills, hp_breakdown, etc.)
        rules_db_path: Path to pathfinder.db. Defaults to server.DB_PATH.

    Returns:
        Dict with all computed stats:
        {
            "ability_mods": {...},
            "hp": {"max": int, "breakdown": {...}},
            "saves": {"fort": int, "ref": int, "will": int},
            "bab": int,
            "ac": {"total": int, "touch": int, "flat_footed": int, ...},
            "cmb_cmd": {"cmb": int, "cmd": int},
            "initiative": {"total": int, "components": {...}},
            "attacks": [...],
            "skills": {...},
            "spell_slots": {...},
        }
    """
    # Extract character components
    abilities = character_data.get("abilities", {})
    classes = character_data.get("classes", [])
    feats = character_data.get("feats", [])
    traits = character_data.get("traits", [])
    skills = character_data.get("skills", {})
    equipment = character_data.get("equipment", [])
    hp_breakdown = character_data.get("hp_breakdown", {})

    # Compute ability modifiers
    ability_mods = {}
    for ability in ("str", "dex", "con", "int", "wis", "cha"):
        score = abilities.get(ability, 10)
        ability_mods[ability] = (score - 10) // 2

    # Look up class data from rules DB
    class_data = {}
    for cls in classes:
        cls_name = cls.get("name", "")
        cd = lookup_class_data(cls_name, rules_db_path)
        if "error" not in cd:
            class_data[cls_name.lower()] = cd

    # Compute each stat block
    hp = compute_hp(classes, class_data, ability_mods, hp_breakdown, feats)
    saves = compute_saves(classes, class_data, ability_mods)
    bab = compute_bab(classes, class_data)
    ac = compute_ac(equipment, ability_mods)
    cmb_cmd = compute_cmb_cmd(bab, ability_mods, equipment)
    initiative = compute_initiative(ability_mods, feats, traits)
    attacks = compute_attack_lines(equipment, bab, ability_mods, feats)
    skill_totals = compute_skill_totals(skills, ability_mods, classes, class_data, equipment)
    spell_slots = compute_spell_slots(classes, class_data, ability_mods)

    return {
        "ability_mods": ability_mods,
        "hp": hp,
        "saves": saves,
        "bab": bab,
        "ac": ac,
        "cmb_cmd": cmb_cmd,
        "initiative": initiative,
        "attacks": attacks,
        "skills": skill_totals,
        "spell_slots": spell_slots,
    }
