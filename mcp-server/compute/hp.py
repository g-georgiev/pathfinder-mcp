"""Hit point computation for Pathfinder 1e characters."""


def compute_hp(
    classes: list[dict],
    class_data: dict,
    ability_mods: dict,
    hp_breakdown: dict,
    feats: list[dict],
) -> dict:
    """Compute maximum HP for a character.

    If hp_breakdown is provided with hit_dice > 0, uses the pre-calculated
    breakdown directly (sum of all fields). Otherwise computes from scratch:
    L1 = max hit die of first class, remaining levels use avg-up (half+1),
    plus CON modifier per level, Toughness feat bonus, and favored class HP.

    Args:
        classes: List of class dicts, e.g. [{"name": "Fighter", "level": 5}]
        class_data: Dict keyed by lowercase class name -> parsed class data
        ability_mods: Dict of ability modifier values, e.g. {"con": 2, ...}
        hp_breakdown: Dict with pre-calculated HP components:
            hit_dice, con, favored_class, toughness, misc
        feats: List of feat dicts, e.g. [{"name": "Toughness", ...}]

    Returns:
        {"max": int, "breakdown": dict} with the total HP and its components.
    """
    # If breakdown is fully provided, use it directly
    if hp_breakdown and hp_breakdown.get("hit_dice", 0) > 0:
        breakdown = {
            "hit_dice": hp_breakdown.get("hit_dice", 0),
            "con": hp_breakdown.get("con", 0),
            "favored_class": hp_breakdown.get("favored_class", 0),
            "toughness": hp_breakdown.get("toughness", 0),
            "misc": hp_breakdown.get("misc", 0),
        }
        total = sum(breakdown.values())
        return {"max": total, "breakdown": breakdown}

    # Compute from scratch
    con_mod = ability_mods.get("con", 0)
    total_level = sum(c.get("level", 1) for c in classes)
    has_toughness = any(
        f.get("name", "").lower() == "toughness" for f in feats
    )

    hit_dice_total = 0
    first_class = True

    for cls in classes:
        cls_name = cls.get("name", "").lower()
        cls_level = cls.get("level", 1)
        cd = class_data.get(cls_name, {})
        hit_die = int(cd.get("hit_die", "8"))

        if first_class:
            # First level of first class gets max hit die
            hit_dice_total += hit_die
            # Remaining levels of this class get avg-up
            remaining = cls_level - 1
            avg_up = (hit_die // 2) + 1
            hit_dice_total += avg_up * remaining
            first_class = False
        else:
            # Multiclass levels get avg-up for all levels
            avg_up = (hit_die // 2) + 1
            hit_dice_total += avg_up * cls_level

    con_total = con_mod * total_level
    toughness_total = total_level if has_toughness else 0

    breakdown = {
        "hit_dice": hit_dice_total,
        "con": con_total,
        "favored_class": 0,
        "toughness": toughness_total,
        "misc": 0,
    }
    total = sum(breakdown.values())

    return {"max": total, "breakdown": breakdown}
