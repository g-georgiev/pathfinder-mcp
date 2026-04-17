"""Saving throw computation for Pathfinder 1e characters."""


def compute_saves(
    classes: list[dict],
    class_data: dict,
    ability_mods: dict,
) -> dict:
    """Compute base saving throw totals.

    Sums each class's cumulative fort/ref/will at their level from the
    progression table, then adds the relevant ability modifier:
    Fort += CON, Ref += DEX, Will += WIS.

    Args:
        classes: List of class dicts, e.g. [{"name": "Fighter", "level": 5}]
        class_data: Dict keyed by lowercase class name -> parsed class data
            with 'progression' list where progression[level-1] has
            {"fort": int, "ref": int, "will": int} (cumulative values).
        ability_mods: Dict of ability modifier values.

    Returns:
        {"fort": int, "ref": int, "will": int} — total save bonuses.
    """
    base_fort = 0
    base_ref = 0
    base_will = 0

    for cls in classes:
        cls_name = cls.get("name", "").lower()
        cls_level = cls.get("level", 1)
        cd = class_data.get(cls_name, {})
        progression = cd.get("progression", [])

        if progression and cls_level >= 1 and cls_level <= len(progression):
            entry = progression[cls_level - 1]
            base_fort += entry.get("fort", 0)
            base_ref += entry.get("ref", 0)
            base_will += entry.get("will", 0)

    return {
        "fort": base_fort + ability_mods.get("con", 0),
        "ref": base_ref + ability_mods.get("dex", 0),
        "will": base_will + ability_mods.get("wis", 0),
    }
