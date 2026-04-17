"""Combat tools — initiative, attacks, saves, skill checks, turn management."""

import json
import random
import re
import uuid

from game_state import get_game_db


def _roll_dice(dice_str: str) -> int:
    """Parse and roll a dice expression like '1d8+5' or '2d6+3'.

    Returns the total rolled value.
    """
    total = 0
    # Match patterns like 2d6, 1d8+5, 1d4-1
    parts = re.findall(r'([+-]?\d*d\d+|[+-]?\d+)', dice_str.replace(" ", ""))
    for part in parts:
        if 'd' in part:
            sign = -1 if part.startswith('-') else 1
            cleaned = part.lstrip('+-')
            num, sides = cleaned.split('d')
            num = int(num) if num else 1
            sides = int(sides)
            for _ in range(num):
                total += sign * random.randint(1, sides)
        else:
            total += int(part)
    return total


def _get_initiative_mod(computed: dict) -> int:
    """Extract initiative modifier from computed JSON."""
    init = computed.get("initiative", {})
    if isinstance(init, dict):
        return init.get("total", 0)
    return 0


def _get_character_name(db, character_id: str) -> str:
    """Look up character name from characters table."""
    row = db.execute("SELECT name FROM characters WHERE id = ?", (character_id,)).fetchone()
    return row["name"] if row else character_id


def start_combat(
    session_id: str,
    combatants: list[dict],
) -> dict:
    """Start a combat encounter with initiative ordering.

    Each combatant needs an initiative roll. The system looks up initiative
    modifiers from the character's computed JSON and sorts by total (descending),
    with ties broken by higher raw roll.

    Args:
        session_id: The session this combat belongs to
        combatants: List of dicts, each with character_id or npc_id and initiative_roll.
                    Example: [{"character_id": "abc123", "initiative_roll": 18}]
    """
    db = get_game_db()
    try:
        ordered = []
        for c in combatants:
            cid = c.get("character_id") or c.get("npc_id", "")
            roll = c.get("initiative_roll", 0)

            # Look up initiative modifier from computed JSON
            modifier = 0
            row = db.execute(
                "SELECT name, computed FROM characters WHERE id = ?", (cid,)
            ).fetchone()
            if row:
                computed = json.loads(row["computed"]) if row["computed"] else {}
                modifier = _get_initiative_mod(computed)

            total = roll + modifier
            ordered.append({
                "id": cid,
                "name": row["name"] if row else cid,
                "roll": roll,
                "modifier": modifier,
                "total": total,
            })

        # Sort: highest total first, ties broken by higher roll
        ordered.sort(key=lambda x: (x["total"], x["roll"]), reverse=True)

        combat_id = uuid.uuid4().hex[:12]
        turn_order_json = json.dumps([e["id"] for e in ordered])

        db.execute(
            "INSERT INTO combats (id, session_id, turn_order) VALUES (?, ?, ?)",
            (combat_id, session_id, turn_order_json),
        )
        db.commit()

        return {
            "combat_id": combat_id,
            "turn_order": ordered,
            "round": 1,
            "current_turn": ordered[0]["id"] if ordered else None,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def get_combat_state(session_id: str) -> dict:
    """Get the current combat state including all combatant summaries.

    Returns turn order with each combatant's name, HP, status, and active conditions.

    Args:
        session_id: The session to query for active combat
    """
    db = get_game_db()
    try:
        combat = db.execute(
            "SELECT * FROM combats WHERE session_id = ? AND status = 'active' ORDER BY started_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if not combat:
            return {"error": "No active combat in this session"}

        combat = dict(combat)
        turn_order_ids = json.loads(combat["turn_order"])
        current_idx = combat["current_turn_index"]

        combatant_details = []
        for cid in turn_order_ids:
            char = db.execute(
                "SELECT id, name, current_hp, max_hp, status FROM characters WHERE id = ?",
                (cid,),
            ).fetchone()
            if char:
                char_dict = dict(char)
                # Get active conditions
                conds = db.execute(
                    "SELECT condition_name, duration_rounds FROM conditions WHERE character_id = ? AND session_id = ?",
                    (cid, session_id),
                ).fetchall()
                char_dict["conditions"] = [
                    {"name": c["condition_name"], "duration": c["duration_rounds"]} for c in conds
                ]
                combatant_details.append(char_dict)
            else:
                combatant_details.append({"id": cid, "name": cid, "conditions": []})

        return {
            "combat_id": combat["id"],
            "round": combat["round"],
            "current_turn": turn_order_ids[current_idx] if turn_order_ids else None,
            "turn_order": combatant_details,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def resolve_attack(
    session_id: str,
    attacker_id: str,
    target_id: str,
    attack_index: int = 0,
    roll: int = 0,
    modifiers: list[str] = [],
) -> dict:
    """Resolve a melee or ranged attack against a target.

    Reads attacker's computed attacks and target's AC. If roll is 0, generates
    a random d20. Applies situational modifiers (flanking, etc.) and determines
    hit/miss, damage, and critical hits.

    Args:
        session_id: The session context
        attacker_id: Character ID of the attacker
        target_id: Character ID of the target
        attack_index: Which attack to use (0 = primary, 1+ = iteratives/secondary)
        roll: The d20 roll (0 = auto-roll)
        modifiers: Situational modifiers like ["flanking", "higher_ground", "prone"]
    """
    db = get_game_db()
    try:
        # Get attacker's computed data
        attacker = db.execute(
            "SELECT name, computed FROM characters WHERE id = ?", (attacker_id,)
        ).fetchone()
        if not attacker:
            return {"error": f"Attacker '{attacker_id}' not found"}

        computed = json.loads(attacker["computed"]) if attacker["computed"] else {}
        attacks = computed.get("attacks", [])

        attack_bonus = 0
        damage_str = "1d6"
        crit_range = 20
        crit_mult = 2

        if attacks and attack_index < len(attacks):
            atk = attacks[attack_index]
            attack_bonus = atk.get("ab", atk.get("attack_bonus", 0))
            damage_str = atk.get("damage", "1d6")
            crit_info = atk.get("crit", "20/x2")
            # Parse crit range like "19-20/x2"
            crit_match = re.match(r'(\d+)(?:-20)?/x(\d+)', str(crit_info))
            if crit_match:
                crit_range = int(crit_match.group(1))
                crit_mult = int(crit_match.group(2))

        # Get target AC
        target = db.execute(
            "SELECT name, computed, current_hp, status FROM characters WHERE id = ?", (target_id,)
        ).fetchone()
        if not target:
            return {"error": f"Target '{target_id}' not found"}

        target_computed = json.loads(target["computed"]) if target["computed"] else {}
        ac_data = target_computed.get("ac", {})
        target_ac = ac_data.get("total", ac_data.get("normal", 10)) if isinstance(ac_data, dict) else 10

        # Roll if not provided
        if roll == 0:
            roll = random.randint(1, 20)

        # Apply situational modifiers
        situational = 0
        modifier_map = {
            "flanking": 2,
            "higher_ground": 1,
            "charge": 2,
            "prone": -4,
        }
        for mod in modifiers:
            situational += modifier_map.get(mod.lower(), 0)

        total = roll + attack_bonus + situational

        # Natural 20 always hits, natural 1 always misses
        nat_20 = roll == 20
        nat_1 = roll == 1
        hit = (nat_20 or total >= target_ac) and not nat_1

        damage = 0
        is_crit = False

        if hit:
            damage = _roll_dice(damage_str)
            damage = max(1, damage)  # minimum 1 on hit

            # Critical hit: natural 20 or roll in crit range
            if roll >= crit_range:
                is_crit = True
                # Roll extra damage for crit multiplier
                for _ in range(crit_mult - 1):
                    damage += max(1, _roll_dice(damage_str))

            # Apply damage to target HP
            new_hp = (target["current_hp"] or 0) - damage
            status = "alive"
            if new_hp <= -10:  # Pathfinder dead threshold (CON-based, simplified)
                status = "dead"
            elif new_hp < 0:
                status = "dying"
            elif new_hp == 0:
                status = "disabled"

            db.execute(
                "UPDATE characters SET current_hp = ?, status = ?, updated_at = datetime('now') WHERE id = ?",
                (new_hp, status, target_id),
            )
            db.commit()
        else:
            new_hp = target["current_hp"] or 0

        return {
            "hit": hit,
            "roll": roll,
            "total": total,
            "ac": target_ac,
            "damage": damage,
            "crit": is_crit,
            "target_hp_remaining": new_hp,
            "target_status": status if hit else (target["status"] if target["status"] else "alive"),
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def resolve_save(
    session_id: str,
    character_id: str,
    save_type: str,
    dc: int,
    roll: int = 0,
) -> dict:
    """Resolve a saving throw for a character.

    Reads the character's computed save bonuses and determines success/failure.

    Args:
        session_id: The session context
        character_id: Character making the save
        save_type: One of 'fort', 'ref', 'will' (or 'fortitude', 'reflex')
        dc: Difficulty class to beat
        roll: The d20 roll (0 = auto-roll)
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT name, computed FROM characters WHERE id = ?", (character_id,)
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        computed = json.loads(row["computed"]) if row["computed"] else {}
        saves = computed.get("saves", {})

        # Normalize save type
        save_key = save_type.lower()
        if save_key == "fortitude":
            save_key = "fort"
        elif save_key == "reflex":
            save_key = "ref"

        save_bonus = 0
        save_data = saves.get(save_key, {})
        if isinstance(save_data, dict):
            save_bonus = save_data.get("total", 0)
        elif isinstance(save_data, (int, float)):
            save_bonus = int(save_data)

        if roll == 0:
            roll = random.randint(1, 20)

        total = roll + save_bonus
        # Natural 20 always succeeds, natural 1 always fails on saves
        success = (roll == 20) or (total >= dc and roll != 1)

        return {
            "success": success,
            "roll": roll,
            "total": total,
            "dc": dc,
            "save_type": save_key,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def resolve_skill_check(
    session_id: str,
    character_id: str,
    skill: str,
    dc: int,
    roll: int = 0,
) -> dict:
    """Resolve a skill check for a character.

    Reads the character's computed skill bonuses and determines success/failure.

    Args:
        session_id: The session context
        character_id: Character making the check
        skill: Skill name (e.g. 'perception', 'stealth', 'knowledge (arcana)')
        dc: Difficulty class to beat
        roll: The d20 roll (0 = auto-roll)
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT name, computed FROM characters WHERE id = ?", (character_id,)
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        computed = json.loads(row["computed"]) if row["computed"] else {}
        skills = computed.get("skills", {})

        skill_key = skill.lower()
        skill_bonus = 0
        skill_data = skills.get(skill_key, {})
        if isinstance(skill_data, dict):
            skill_bonus = skill_data.get("total", 0)
        elif isinstance(skill_data, (int, float)):
            skill_bonus = int(skill_data)

        if roll == 0:
            roll = random.randint(1, 20)

        total = roll + skill_bonus
        # Skill checks: natural 20 and 1 are not auto-success/fail in Pathfinder
        success = total >= dc

        return {
            "success": success,
            "roll": roll,
            "total": total,
            "dc": dc,
            "skill": skill_key,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def advance_turn(session_id: str) -> dict:
    """Advance combat to the next combatant's turn.

    Increments the turn index (wrapping to round start), increments the round
    counter on wrap, and decrements/expires duration-based conditions.

    Args:
        session_id: The session with active combat
    """
    db = get_game_db()
    try:
        combat = db.execute(
            "SELECT * FROM combats WHERE session_id = ? AND status = 'active' ORDER BY started_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if not combat:
            return {"error": "No active combat in this session"}

        combat = dict(combat)
        turn_order = json.loads(combat["turn_order"])
        current_idx = combat["current_turn_index"]
        current_round = combat["round"]

        # Advance
        next_idx = current_idx + 1
        if next_idx >= len(turn_order):
            next_idx = 0
            current_round += 1

        # Update combat
        db.execute(
            "UPDATE combats SET current_turn_index = ?, round = ? WHERE id = ?",
            (next_idx, current_round, combat["id"]),
        )

        # Decrement conditions with finite durations
        expired = []
        conditions = db.execute(
            "SELECT * FROM conditions WHERE session_id = ? AND duration_rounds > 0",
            (session_id,),
        ).fetchall()
        for cond in conditions:
            new_dur = cond["duration_rounds"] - 1
            if new_dur <= 0:
                expired.append({
                    "character_id": cond["character_id"],
                    "condition": cond["condition_name"],
                })
                db.execute("DELETE FROM conditions WHERE id = ?", (cond["id"],))
            else:
                db.execute(
                    "UPDATE conditions SET duration_rounds = ? WHERE id = ?",
                    (new_dur, cond["id"]),
                )

        db.commit()

        current_id = turn_order[next_idx] if turn_order else None
        current_name = _get_character_name(db, current_id) if current_id else None

        return {
            "round": current_round,
            "current_turn_id": current_id,
            "current_turn_name": current_name,
            "conditions_expired": expired,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def end_combat(
    session_id: str,
    xp_award: int = 0,
    loot: list[dict] = [],
) -> dict:
    """End the active combat encounter.

    Sets combat status to 'ended'. Optionally divides XP equally among player
    characters and logs loot (loot is not auto-distributed — DM decides).

    Args:
        session_id: The session with active combat
        xp_award: Total XP to divide among player characters (0 = no XP)
        loot: List of loot items (e.g. [{"name": "Longsword +1", "value": 2315}])
    """
    db = get_game_db()
    try:
        combat = db.execute(
            "SELECT * FROM combats WHERE session_id = ? AND status = 'active' ORDER BY started_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if not combat:
            return {"error": "No active combat in this session"}

        combat = dict(combat)
        db.execute(
            "UPDATE combats SET status = 'ended' WHERE id = ?", (combat["id"],)
        )

        xp_per_char = 0
        if xp_award > 0:
            # Get player characters in this session
            pcs = db.execute(
                "SELECT id, data FROM characters WHERE session_id = ? AND is_npc = 0",
                (session_id,),
            ).fetchall()
            if pcs:
                xp_per_char = xp_award // len(pcs)
                for pc in pcs:
                    data = json.loads(pc["data"]) if pc["data"] else {}
                    data["xp"] = data.get("xp", 0) + xp_per_char
                    db.execute(
                        "UPDATE characters SET data = ?, updated_at = datetime('now') WHERE id = ?",
                        (json.dumps(data), pc["id"]),
                    )

        db.commit()

        return {
            "combat_id": combat["id"],
            "rounds_fought": combat["round"],
            "xp_per_character": xp_per_char,
            "loot": loot,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
