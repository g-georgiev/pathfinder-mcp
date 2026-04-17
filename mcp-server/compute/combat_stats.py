"""Combat stat computation for Pathfinder 1e characters.

Covers BAB, AC, CMB/CMD, initiative, and attack line generation.
"""


def compute_bab(classes: list[dict], class_data: dict) -> int:
    """Compute total Base Attack Bonus by summing each class's BAB.

    Args:
        classes: List of class dicts with "name" and "level".
        class_data: Dict keyed by lowercase class name -> parsed class data.

    Returns:
        Total BAB as an integer.
    """
    total = 0
    for cls in classes:
        cls_name = cls.get("name", "").lower()
        cls_level = cls.get("level", 1)
        cd = class_data.get(cls_name, {})
        progression = cd.get("progression", [])
        if progression and 1 <= cls_level <= len(progression):
            total += progression[cls_level - 1].get("bab", 0)
    return total


def compute_ac(equipment: list[dict], ability_mods: dict) -> dict:
    """Compute Armor Class breakdown.

    Sums equipment bonuses by type (armor, shield, deflection, natural,
    insight, dodge). Applies max_dex cap from armor/shield. Touch AC
    excludes armor/shield/natural. Flat-footed excludes DEX/dodge.

    Args:
        equipment: List of equipment dicts with "stats" sub-dict.
        ability_mods: Ability modifier dict.

    Returns:
        {"total": int, "touch": int, "flat_footed": int, "components": dict}
    """
    components = {
        "base": 10,
        "armor": 0,
        "shield": 0,
        "dex": 0,
        "natural": 0,
        "deflection": 0,
        "dodge": 0,
        "insight": 0,
        "misc": 0,
    }

    max_dex = 999  # Effectively unlimited unless capped by armor

    for item in equipment:
        stats = item.get("stats", {})
        item_type = stats.get("type", "")
        ac_bonus = stats.get("ac_bonus", 0)

        if item_type == "armor":
            components["armor"] += ac_bonus
            item_max_dex = stats.get("max_dex")
            if item_max_dex is not None:
                max_dex = min(max_dex, item_max_dex)
        elif item_type == "shield":
            components["shield"] += ac_bonus
            item_max_dex = stats.get("max_dex")
            if item_max_dex is not None:
                max_dex = min(max_dex, item_max_dex)
        elif item_type == "natural":
            components["natural"] += ac_bonus
        elif item_type == "deflection":
            components["deflection"] += ac_bonus
        elif item_type == "dodge":
            components["dodge"] += ac_bonus
        elif item_type == "insight":
            components["insight"] += ac_bonus

    dex_mod = ability_mods.get("dex", 0)
    effective_dex = min(dex_mod, max_dex)
    components["dex"] = effective_dex

    total = sum(components.values())

    # Touch AC: exclude armor, shield, natural
    touch = total - components["armor"] - components["shield"] - components["natural"]

    # Flat-footed: exclude DEX and dodge
    flat_footed = total - components["dex"] - components["dodge"]

    return {
        "total": total,
        "touch": touch,
        "flat_footed": flat_footed,
        "components": components,
    }


def compute_cmb_cmd(
    bab: int,
    ability_mods: dict,
    equipment: list[dict] = None,
) -> dict:
    """Compute Combat Maneuver Bonus and Defense.

    CMB = BAB + STR mod (+ size modifier, not tracked here)
    CMD = 10 + BAB + STR mod + DEX mod (+ size modifier)

    Args:
        bab: Base Attack Bonus.
        ability_mods: Ability modifier dict.
        equipment: Equipment list (unused currently, placeholder for future).

    Returns:
        {"cmb": int, "cmd": int}
    """
    if equipment is None:
        equipment = []
    str_mod = ability_mods.get("str", 0)
    dex_mod = ability_mods.get("dex", 0)

    cmb = bab + str_mod
    cmd = 10 + bab + str_mod + dex_mod

    return {"cmb": cmb, "cmd": cmd}


def compute_initiative(
    ability_mods: dict,
    feats: list[dict],
    traits: list[dict],
) -> dict:
    """Compute initiative modifier.

    Base = DEX mod. Improved Initiative feat adds +4.
    Reactionary trait adds +2.

    Args:
        ability_mods: Ability modifier dict.
        feats: List of feat dicts.
        traits: List of trait dicts.

    Returns:
        {"total": int, "components": dict}
    """
    dex_mod = ability_mods.get("dex", 0)
    components = {"dex": dex_mod}

    for feat in feats:
        if feat.get("name", "").lower() == "improved initiative":
            components["improved_initiative"] = 4
            break

    for trait in traits:
        name = trait.get("name", "").lower()
        if name == "reactionary":
            components["reactionary"] = 2
            break

    total = sum(components.values())
    return {"total": total, "components": components}


def compute_attack_lines(
    equipment: list[dict],
    bab: int,
    ability_mods: dict,
    feats: list[dict] = None,
) -> list[dict]:
    """Compute attack lines for each weapon in equipment.

    For each weapon: AB = bab + ability_mod (STR for melee, DEX for ranged)
    + enhancement bonus. Generates iterative attacks at bab-5, bab-10, etc.
    Damage = weapon damage dice + ability_mod + enhancement + weapon
    specialization (+2 if applicable feat).

    Args:
        equipment: List of equipment dicts.
        bab: Base Attack Bonus.
        ability_mods: Ability modifier dict.
        feats: List of feat dicts.

    Returns:
        List of attack line dicts:
        [{"name": str, "ab": [list], "damage": str, "crit": str, "notes": []}]
    """
    if feats is None:
        feats = []

    attack_lines = []

    # Check for Weapon Specialization feat
    has_weapon_spec = any(
        "weapon specialization" in f.get("name", "").lower() for f in feats
    )
    has_power_attack = any(
        f.get("name", "").lower() == "power attack" for f in feats
    )

    for item in equipment:
        stats = item.get("stats", {})
        if stats.get("type") not in ("melee", "ranged"):
            continue

        weapon_type = stats.get("type", "melee")
        damage_dice = stats.get("damage", "1d8")
        crit = stats.get("crit", "20/x2")
        enhancement = stats.get("enhancement", 0)

        # Determine ability modifier for attack and damage
        ability_key = stats.get("ability", "str" if weapon_type == "melee" else "dex")
        atk_mod = ability_mods.get(ability_key, 0)

        # For damage, melee uses STR, ranged generally doesn't add STR
        # unless composite bow or thrown. Default: melee=STR, ranged=0
        if weapon_type == "melee":
            dmg_ability_mod = ability_mods.get("str", 0)
        else:
            # Ranged weapons don't add STR to damage by default
            # (composite bows would specify this in stats)
            dmg_ability_key = stats.get("damage_ability")
            dmg_ability_mod = ability_mods.get(dmg_ability_key, 0) if dmg_ability_key else 0

        # Attack bonus
        base_ab = bab + atk_mod + enhancement

        # Generate iterative attacks
        iteratives = [base_ab]
        if bab >= 6:
            iteratives.append(base_ab - 5)
        if bab >= 11:
            iteratives.append(base_ab - 10)
        if bab >= 16:
            iteratives.append(base_ab - 15)

        # Damage
        total_dmg_bonus = dmg_ability_mod + enhancement
        if has_weapon_spec:
            total_dmg_bonus += 2

        if total_dmg_bonus > 0:
            damage_str = f"{damage_dice}+{total_dmg_bonus}"
        elif total_dmg_bonus < 0:
            damage_str = f"{damage_dice}{total_dmg_bonus}"
        else:
            damage_str = damage_dice

        notes = []
        if has_power_attack:
            # Power Attack penalty/bonus scales with BAB
            pa_penalty = 1 + (bab // 4)
            pa_bonus = 2 + 2 * (bab // 4)
            notes.append(f"Power Attack: -{pa_penalty} AB/+{pa_bonus} damage")

        attack_lines.append({
            "name": item.get("name", "Unknown Weapon"),
            "ab": iteratives,
            "damage": damage_str,
            "crit": crit,
            "notes": notes,
        })

    return attack_lines
