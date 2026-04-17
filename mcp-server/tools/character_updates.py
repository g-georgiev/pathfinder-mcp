"""Character update tools — HP, conditions, inventory, spells, level-up."""

import json

from game_state import get_game_db
from compute.derived import compute_derived_stats


def update_character_hp(
    session_id: str,
    character_id: str,
    delta: int,
    source: str = "",
) -> dict:
    """Apply HP change to a character and update their status.

    Clamps HP between -CON_score and max_hp. Updates status:
    alive (hp > 0), unconscious (hp == 0), dying (hp < 0),
    dead (hp <= -CON_score).

    Args:
        session_id: The session the character belongs to
        character_id: The character's unique identifier
        delta: HP change (positive = healing, negative = damage)
        source: Description of what caused the change

    Returns:
        dict with character_id, current_hp, max_hp, delta, status, source.
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        current_hp = row["current_hp"]
        max_hp = row["max_hp"]

        # Get CON score for death threshold
        data = json.loads(row["data"] or "{}")
        abilities = data.get("abilities", {})
        con_score = abilities.get("con", 10)

        # Apply delta and clamp
        new_hp = current_hp + delta
        new_hp = max(-con_score, min(max_hp, new_hp))

        # Determine status
        if new_hp > 0:
            status = "alive"
        elif new_hp == 0:
            status = "unconscious"
        elif new_hp <= -con_score:
            status = "dead"
        else:
            status = "dying"

        db.execute(
            "UPDATE characters SET current_hp = ?, status = ?, updated_at = datetime('now') "
            "WHERE id = ? AND session_id = ?",
            (new_hp, status, character_id, session_id),
        )
        db.commit()

        return {
            "character_id": character_id,
            "current_hp": new_hp,
            "max_hp": max_hp,
            "delta": delta,
            "status": status,
            "source": source,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def update_character_conditions(
    session_id: str,
    character_id: str,
    add: list[dict] = None,
    remove: list[str] = None,
) -> dict:
    """Add or remove conditions on a character.

    Args:
        session_id: The session the character belongs to
        character_id: The character's unique identifier
        add: List of condition dicts to add, each with:
            name (str), duration_rounds (int, -1=permanent), source (str)
        remove: List of condition names to remove

    Returns:
        dict with character_id and current conditions list.
    """
    if add is None:
        add = []
    if remove is None:
        remove = []

    db = get_game_db()
    try:
        row = db.execute(
            "SELECT id FROM characters WHERE id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        # Remove conditions by name
        for cond_name in remove:
            db.execute(
                "DELETE FROM conditions WHERE character_id = ? AND session_id = ? "
                "AND condition_name = ?",
                (character_id, session_id, cond_name),
            )

        # Add new conditions
        for cond in add:
            db.execute(
                "INSERT INTO conditions (session_id, character_id, condition_name, "
                "duration_rounds, source) VALUES (?, ?, ?, ?, ?)",
                (
                    session_id,
                    character_id,
                    cond.get("name", "unknown"),
                    cond.get("duration_rounds", -1),
                    cond.get("source", ""),
                ),
            )

        db.commit()

        # Return current conditions
        conditions = db.execute(
            "SELECT * FROM conditions WHERE character_id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchall()

        return {
            "character_id": character_id,
            "conditions": [
                {
                    "name": c["condition_name"],
                    "duration_rounds": c["duration_rounds"],
                    "source": c["source"],
                }
                for c in conditions
            ],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def update_character_inventory(
    session_id: str,
    character_id: str,
    add: list[dict] = None,
    remove: list[dict] = None,
    gold_delta: int = 0,
) -> dict:
    """Modify a character's inventory and gold.

    Reads the character data JSON, modifies the equipment list and gold
    value, then writes back.

    Args:
        session_id: The session the character belongs to
        character_id: The character's unique identifier
        add: List of item dicts to add to equipment
        remove: List of item dicts to remove (matched by "name" field)
        gold_delta: Amount to add/subtract from gold

    Returns:
        dict with character_id, inventory list, and gold total.
    """
    if add is None:
        add = []
    if remove is None:
        remove = []

    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        data = json.loads(row["data"] or "{}")
        equipment = data.get("equipment", [])
        gold = data.get("gold", 0)

        # Remove items by name
        remove_names = {item.get("name", "").lower() for item in remove}
        equipment = [
            item for item in equipment
            if item.get("name", "").lower() not in remove_names
        ]

        # Add new items
        equipment.extend(add)

        # Update gold
        gold += gold_delta

        # Write back
        data["equipment"] = equipment
        data["gold"] = gold

        db.execute(
            "UPDATE characters SET data = ?, updated_at = datetime('now') "
            "WHERE id = ? AND session_id = ?",
            (json.dumps(data), character_id, session_id),
        )
        db.commit()

        return {
            "character_id": character_id,
            "inventory": equipment,
            "gold": gold,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def update_character_spells(
    session_id: str,
    character_id: str,
    cast: str = "",
    restore_slot: int = -1,
) -> dict:
    """Track spell slot usage for a character.

    Maintains a "spell_slots_used" dict in the character's data blob,
    keyed by spell level string. Casting increments the used count;
    restoring decrements it.

    Args:
        session_id: The session the character belongs to
        character_id: The character's unique identifier
        cast: Spell level string to cast (e.g. "1", "3") — increments used
        restore_slot: Spell level to restore (e.g. 1, 3) — decrements used

    Returns:
        dict with character_id and spell_slots breakdown:
        {level: {total, used, remaining}} for each level.
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        data = json.loads(row["data"] or "{}")
        computed = json.loads(row["computed"] or "{}")
        spell_slots_used = data.get("spell_slots_used", {})

        # Get total slots from computed
        all_slots = computed.get("spell_slots", {})

        # Cast: increment used count for the spell level
        if cast:
            level_key = str(cast)
            current_used = spell_slots_used.get(level_key, 0)
            spell_slots_used[level_key] = current_used + 1

        # Restore: decrement used count for the spell level
        if restore_slot >= 0:
            level_key = str(restore_slot)
            current_used = spell_slots_used.get(level_key, 0)
            spell_slots_used[level_key] = max(0, current_used - 1)

        # Write back
        data["spell_slots_used"] = spell_slots_used
        db.execute(
            "UPDATE characters SET data = ?, updated_at = datetime('now') "
            "WHERE id = ? AND session_id = ?",
            (json.dumps(data), character_id, session_id),
        )
        db.commit()

        # Build response with total/used/remaining per level per class
        result_slots = {}
        for cls_name, slots in all_slots.items():
            for level_str, total in slots.items():
                used = spell_slots_used.get(level_str, 0)
                result_slots[level_str] = {
                    "total": total,
                    "used": used,
                    "remaining": max(0, total - used),
                }

        return {
            "character_id": character_id,
            "spell_slots": result_slots,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def apply_level_up(
    session_id: str,
    character_id: str,
    level_up_data: dict,
) -> dict:
    """Apply level-up changes to a character.

    Reads the character data, applies level-up modifications (class level
    increment, new feats, skill ranks, class options), then re-runs
    compute_derived_stats to update the computed column.

    Args:
        session_id: The session the character belongs to
        character_id: The character's unique identifier
        level_up_data: Dict describing the level-up:
            class_name (str): Which class gains the level
            new_feats (list[dict]): Feats gained at this level
            skill_ranks (dict): skill_name -> additional ranks
            hp_roll (int): HP gained from hit die roll
            class_options (list[dict]): Class-specific choices
            ability_increase (dict): {"ability": str, "amount": int} for L4/8/12/etc

    Returns:
        Updated character dict with new computed stats.
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        data = json.loads(row["data"] or "{}")
        classes = data.get("classes", [])

        # Increment class level
        target_class = level_up_data.get("class_name", "")
        class_found = False
        for cls in classes:
            if cls.get("name", "").lower() == target_class.lower():
                cls["level"] = cls.get("level", 1) + 1
                class_found = True
                break

        if not class_found:
            # New class (multiclassing)
            classes.append({"name": target_class, "level": 1})

        data["classes"] = classes

        # Add new feats
        new_feats = level_up_data.get("new_feats", [])
        existing_feats = data.get("feats", [])
        existing_feats.extend(new_feats)
        data["feats"] = existing_feats

        # Add skill ranks
        new_skill_ranks = level_up_data.get("skill_ranks", {})
        existing_skills = data.get("skills", {})
        for skill, ranks in new_skill_ranks.items():
            existing_skills[skill] = existing_skills.get(skill, 0) + ranks
        data["skills"] = existing_skills

        # Apply HP roll to breakdown
        hp_roll = level_up_data.get("hp_roll", 0)
        if hp_roll > 0:
            hp_breakdown = data.get("hp_breakdown", {})
            hp_breakdown["hit_dice"] = hp_breakdown.get("hit_dice", 0) + hp_roll
            # Add CON to HP breakdown
            con_mod = (data.get("abilities", {}).get("con", 10) - 10) // 2
            hp_breakdown["con"] = hp_breakdown.get("con", 0) + con_mod
            data["hp_breakdown"] = hp_breakdown

        # Apply ability increase (L4, L8, L12, etc.)
        ability_increase = level_up_data.get("ability_increase", {})
        if ability_increase:
            ability_name = ability_increase.get("ability", "").lower()
            amount = ability_increase.get("amount", 1)
            abilities = data.get("abilities", {})
            if ability_name in abilities:
                abilities[ability_name] += amount
            data["abilities"] = abilities

        # Add class options
        class_options = level_up_data.get("class_options", [])
        existing_options = data.get("class_features", [])
        existing_options.extend(class_options)
        data["class_features"] = existing_options

        # Recompute derived stats
        computed = compute_derived_stats(data)

        # Update total level and classes string
        total_level = sum(c.get("level", 1) for c in classes)
        classes_str = ", ".join(
            f"{c.get('name', '?')} {c.get('level', 1)}" for c in classes
        )
        max_hp = computed.get("hp", {}).get("max", 0)

        db.execute(
            """UPDATE characters
               SET data = ?, computed = ?, level = ?, classes = ?,
                   max_hp = ?, current_hp = MIN(current_hp + ?, ?),
                   updated_at = datetime('now')
               WHERE id = ? AND session_id = ?""",
            (
                json.dumps(data), json.dumps(computed),
                total_level, classes_str, max_hp,
                hp_roll + (data.get("abilities", {}).get("con", 10) - 10) // 2,
                max_hp,
                character_id, session_id,
            ),
        )
        db.commit()

        return {
            "character_id": character_id,
            "name": data.get("name", ""),
            "level": total_level,
            "classes": classes_str,
            "computed": computed,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
