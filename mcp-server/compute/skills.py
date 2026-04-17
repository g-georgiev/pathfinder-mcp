"""Skill total computation for Pathfinder 1e characters."""

# Mapping of skill names to their key ability score
SKILL_ABILITY_MAP = {
    # STR skills
    "climb": "str",
    "swim": "str",
    # DEX skills
    "acrobatics": "dex",
    "disable device": "dex",
    "escape artist": "dex",
    "fly": "dex",
    "ride": "dex",
    "sleight of hand": "dex",
    "stealth": "dex",
    # INT skills
    "appraise": "int",
    "craft": "int",
    "knowledge (arcana)": "int",
    "knowledge (dungeoneering)": "int",
    "knowledge (engineering)": "int",
    "knowledge (geography)": "int",
    "knowledge (history)": "int",
    "knowledge (local)": "int",
    "knowledge (nature)": "int",
    "knowledge (nobility)": "int",
    "knowledge (planes)": "int",
    "knowledge (religion)": "int",
    "linguistics": "int",
    "spellcraft": "int",
    # WIS skills
    "heal": "wis",
    "perception": "wis",
    "profession": "wis",
    "sense motive": "wis",
    "survival": "wis",
    # CHA skills
    "bluff": "cha",
    "diplomacy": "cha",
    "disguise": "cha",
    "handle animal": "cha",
    "intimidate": "cha",
    "perform": "cha",
    "use magic device": "cha",
}


def _get_all_class_skills(classes: list[dict], class_data: dict) -> set:
    """Gather class skills from all classes the character has."""
    result = set()
    for cls in classes:
        cls_name = cls.get("name", "").lower()
        cd = class_data.get(cls_name, {})
        for skill in cd.get("class_skills", []):
            result.add(skill.lower())
    return result


def _get_equipment_skill_bonuses(equipment: list[dict]) -> dict:
    """Extract skill bonuses from equipment.

    Looks for equipment with stats.skill_bonuses dict mapping
    skill names to bonus values.
    """
    bonuses = {}
    for item in equipment:
        stats = item.get("stats", {})
        skill_bonuses = stats.get("skill_bonuses", {})
        for skill, bonus in skill_bonuses.items():
            skill_lower = skill.lower()
            bonuses[skill_lower] = bonuses.get(skill_lower, 0) + bonus
    return bonuses


def compute_skill_totals(
    skills: dict,
    ability_mods: dict,
    classes: list[dict],
    class_data: dict,
    equipment: list[dict] = None,
) -> dict:
    """Compute total skill bonuses for all skills with ranks.

    For each skill with ranks > 0:
    total = ranks + ability_mod(key_ability) + 3 (if class skill) + item_bonus

    Args:
        skills: Dict of skill_name -> ranks invested.
        ability_mods: Dict of ability modifiers.
        classes: List of class dicts.
        class_data: Dict keyed by lowercase class name -> parsed class data.
        equipment: List of equipment dicts (optional).

    Returns:
        Dict of skill_name -> total bonus (only skills with ranks > 0).
    """
    if equipment is None:
        equipment = []

    class_skills = _get_all_class_skills(classes, class_data)
    equip_bonuses = _get_equipment_skill_bonuses(equipment)
    totals = {}

    for skill_name, ranks in skills.items():
        if ranks <= 0:
            continue

        skill_lower = skill_name.lower()
        key_ability = SKILL_ABILITY_MAP.get(skill_lower, "int")
        ability_mod = ability_mods.get(key_ability, 0)

        # Class skill bonus: +3 if at least 1 rank and it's a class skill
        is_class_skill = skill_lower in class_skills
        class_bonus = 3 if is_class_skill else 0

        # Item bonus from equipment
        item_bonus = equip_bonuses.get(skill_lower, 0)

        total = ranks + ability_mod + class_bonus + item_bonus
        totals[skill_name] = total

    return totals
