"""Tests for combat tools — initiative, attacks, saves, skills, turns."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import game_state
from tools.session import create_session
from tools.combat import (
    start_combat, get_combat_state, resolve_attack, resolve_save,
    resolve_skill_check, advance_turn, end_combat,
)


def _setup_combat_session(db):
    """Create a session with two characters pre-loaded for combat tests.

    Returns (session_id, fighter_id, goblin_id).
    """
    db.execute(
        "INSERT INTO sessions (id, name) VALUES (?, ?)",
        ("combat-sess", "Combat Test"),
    )
    # Fighter PC with computed stats
    fighter_computed = json.dumps({
        "initiative": {"total": 2},
        "ac": {"total": 22, "touch": 12, "flat_footed": 20},
        "saves": {"fort": {"total": 7}, "ref": {"total": 3}, "will": {"total": 2}},
        "skills": {"perception": {"total": 5}, "climb": {"total": 8}},
        "attacks": [
            {"name": "Longsword +1", "ab": 10, "damage": "1d8+7", "crit": "19-20/x2"},
            {"name": "Longbow", "ab": 6, "damage": "1d8+1", "crit": "20/x3"},
        ],
    })
    db.execute(
        "INSERT INTO characters (id, session_id, player_id, name, level, current_hp, max_hp, is_npc, computed) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("fighter-1", "combat-sess", None, "Valeros", 5, 53, 53, 0, fighter_computed),
    )
    # Goblin NPC with computed stats
    goblin_computed = json.dumps({
        "initiative": {"total": 6},
        "ac": {"total": 16},
        "saves": {"fort": {"total": 3}, "ref": {"total": 4}, "will": {"total": -1}},
        "skills": {"stealth": {"total": 10}, "perception": {"total": 2}},
        "attacks": [
            {"name": "Short Sword", "ab": 2, "damage": "1d4+1", "crit": "19-20/x2"},
        ],
    })
    db.execute(
        "INSERT INTO characters (id, session_id, player_id, name, level, current_hp, max_hp, is_npc, computed) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("goblin-1", "combat-sess", None, "Goblin Warrior", 1, 6, 6, 1, goblin_computed),
    )
    db.commit()
    return "combat-sess", "fighter-1", "goblin-1"


# ---------- Initiative / Start Combat ----------

def test_start_combat_ordering(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)

    # Fighter rolls 15 (15+2=17), Goblin rolls 10 (10+6=16)
    result = start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 15},
        {"character_id": goblin_id, "initiative_roll": 10},
    ])
    assert "error" not in result
    assert result["round"] == 1
    # Fighter total 17 > Goblin total 16
    assert result["turn_order"][0]["id"] == fighter_id
    assert result["turn_order"][0]["total"] == 17
    assert result["turn_order"][1]["id"] == goblin_id
    assert result["turn_order"][1]["total"] == 16
    assert result["current_turn"] == fighter_id


def test_start_combat_tie_breaking(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)

    # Same total (12+2=14 vs 8+6=14), but fighter rolled higher raw -> fighter first
    result = start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 12},
        {"character_id": goblin_id, "initiative_roll": 8},
    ])
    assert result["turn_order"][0]["total"] == result["turn_order"][1]["total"]
    assert result["turn_order"][0]["id"] == fighter_id  # higher roll wins tie


# ---------- Get Combat State ----------

def test_get_combat_state(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    result = get_combat_state(sid)
    assert "error" not in result
    assert result["round"] == 1
    assert len(result["turn_order"]) == 2
    # First combatant should have HP info
    first = result["turn_order"][0]
    assert first["name"] == "Valeros"
    assert first["max_hp"] == 53


def test_get_combat_state_no_combat(game_db):
    sid, _, _ = _setup_combat_session(game_db)
    result = get_combat_state(sid)
    assert "error" in result


# ---------- Resolve Attack ----------

def test_resolve_attack_hit(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Fighter attacks goblin with a roll of 15: 15 + 10 = 25 vs AC 16 -> hit
    result = resolve_attack(sid, fighter_id, goblin_id, attack_index=0, roll=15)
    assert "error" not in result
    assert result["hit"] is True
    assert result["roll"] == 15
    assert result["total"] == 25
    assert result["ac"] == 16
    assert result["damage"] > 0
    assert result["target_hp_remaining"] < 6


def test_resolve_attack_miss(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Goblin attacks fighter with roll of 3: 3 + 2 = 5 vs AC 22 -> miss
    result = resolve_attack(sid, goblin_id, fighter_id, attack_index=0, roll=3)
    assert "error" not in result
    assert result["hit"] is False
    assert result["damage"] == 0
    assert result["target_hp_remaining"] == 53  # unchanged


def test_resolve_attack_nat1_always_misses(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Natural 1 always misses even if total >= AC
    result = resolve_attack(sid, fighter_id, goblin_id, attack_index=0, roll=1)
    assert result["hit"] is False


def test_resolve_attack_nat20_always_hits(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Natural 20 always hits, also a crit threat (crit range 19-20)
    result = resolve_attack(sid, goblin_id, fighter_id, attack_index=0, roll=20)
    assert result["hit"] is True
    assert result["crit"] is True  # 20 >= 19 crit range


def test_resolve_attack_with_flanking(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Roll 4 + AB 10 = 14 (miss vs AC 16), but flanking adds +2 -> 16 = hit
    result = resolve_attack(sid, fighter_id, goblin_id, attack_index=0, roll=4, modifiers=["flanking"])
    assert result["hit"] is True
    assert result["total"] == 16  # 4 + 10 + 2


# ---------- Resolve Save ----------

def test_resolve_save_pass(game_db):
    sid, fighter_id, _ = _setup_combat_session(game_db)

    # Fort save: roll 10 + bonus 7 = 17 vs DC 15 -> pass
    result = resolve_save(sid, fighter_id, "fort", dc=15, roll=10)
    assert "error" not in result
    assert result["success"] is True
    assert result["total"] == 17
    assert result["save_type"] == "fort"


def test_resolve_save_fail(game_db):
    sid, _, goblin_id = _setup_combat_session(game_db)

    # Will save: roll 5 + bonus -1 = 4 vs DC 14 -> fail
    result = resolve_save(sid, goblin_id, "will", dc=14, roll=5)
    assert result["success"] is False
    assert result["total"] == 4


def test_resolve_save_nat20_auto_success(game_db):
    sid, _, goblin_id = _setup_combat_session(game_db)

    # Natural 20 always succeeds
    result = resolve_save(sid, goblin_id, "will", dc=30, roll=20)
    assert result["success"] is True


def test_resolve_save_nat1_auto_fail(game_db):
    sid, fighter_id, _ = _setup_combat_session(game_db)

    # Natural 1 always fails even with high bonus
    result = resolve_save(sid, fighter_id, "fort", dc=1, roll=1)
    assert result["success"] is False


def test_resolve_save_full_name(game_db):
    sid, fighter_id, _ = _setup_combat_session(game_db)

    # Should accept "fortitude" and normalize to "fort"
    result = resolve_save(sid, fighter_id, "fortitude", dc=15, roll=10)
    assert result["save_type"] == "fort"
    assert result["success"] is True


# ---------- Resolve Skill Check ----------

def test_resolve_skill_check_pass(game_db):
    sid, fighter_id, _ = _setup_combat_session(game_db)

    # Perception: roll 12 + 5 = 17 vs DC 15 -> pass
    result = resolve_skill_check(sid, fighter_id, "perception", dc=15, roll=12)
    assert "error" not in result
    assert result["success"] is True
    assert result["total"] == 17
    assert result["skill"] == "perception"


def test_resolve_skill_check_fail(game_db):
    sid, fighter_id, _ = _setup_combat_session(game_db)

    # Perception: roll 5 + 5 = 10 vs DC 15 -> fail
    result = resolve_skill_check(sid, fighter_id, "perception", dc=15, roll=5)
    assert result["success"] is False
    assert result["total"] == 10


def test_resolve_skill_check_no_ranks(game_db):
    sid, fighter_id, _ = _setup_combat_session(game_db)

    # Skill not in computed -> bonus is 0
    result = resolve_skill_check(sid, fighter_id, "diplomacy", dc=10, roll=12)
    assert result["success"] is True
    assert result["total"] == 12  # roll + 0


# ---------- Advance Turn ----------

def test_advance_turn_basic(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # First turn is fighter; advance to goblin
    result = advance_turn(sid)
    assert "error" not in result
    assert result["round"] == 1
    assert result["current_turn_id"] == goblin_id
    assert result["current_turn_name"] == "Goblin Warrior"


def test_advance_turn_wraps_round(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Advance twice: fighter -> goblin -> fighter (round 2)
    advance_turn(sid)  # -> goblin, round 1
    result = advance_turn(sid)  # -> fighter, round 2
    assert result["round"] == 2
    assert result["current_turn_id"] == fighter_id


def test_advance_turn_expires_conditions(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Add a condition with 1 round remaining
    db = game_state.get_game_db()
    db.execute(
        "INSERT INTO conditions (session_id, character_id, condition_name, duration_rounds, source) "
        "VALUES (?, ?, ?, ?, ?)",
        (sid, fighter_id, "Bless", 1, "cleric"),
    )
    # Add a permanent condition (duration -1)
    db.execute(
        "INSERT INTO conditions (session_id, character_id, condition_name, duration_rounds, source) "
        "VALUES (?, ?, ?, ?, ?)",
        (sid, goblin_id, "Fatigued", -1, "exhaustion"),
    )
    db.commit()
    db.close()

    result = advance_turn(sid)
    assert len(result["conditions_expired"]) == 1
    assert result["conditions_expired"][0]["condition"] == "Bless"

    # Permanent condition should still exist
    db = game_state.get_game_db()
    conds = db.execute(
        "SELECT * FROM conditions WHERE session_id = ? AND character_id = ?",
        (sid, goblin_id),
    ).fetchall()
    assert len(conds) == 1
    assert conds[0]["condition_name"] == "Fatigued"
    db.close()


def test_advance_turn_no_combat(game_db):
    sid, _, _ = _setup_combat_session(game_db)
    result = advance_turn(sid)
    assert "error" in result


# ---------- End Combat ----------

def test_end_combat_basic(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    result = end_combat(sid)
    assert "error" not in result
    assert result["combat_id"] is not None
    assert result["rounds_fought"] == 1
    assert result["xp_per_character"] == 0

    # Combat should no longer be active
    state = get_combat_state(sid)
    assert "error" in state  # no active combat


def test_end_combat_with_xp(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    # Award 400 XP, only fighter is a PC (is_npc=0)
    result = end_combat(sid, xp_award=400)
    assert result["xp_per_character"] == 400  # all to 1 PC

    # Verify XP was added to character data
    db = game_state.get_game_db()
    row = db.execute("SELECT data FROM characters WHERE id = ?", (fighter_id,)).fetchone()
    data = json.loads(row["data"])
    assert data["xp"] == 400
    db.close()


def test_end_combat_with_loot(game_db):
    sid, fighter_id, goblin_id = _setup_combat_session(game_db)
    start_combat(sid, [
        {"character_id": fighter_id, "initiative_roll": 18},
        {"character_id": goblin_id, "initiative_roll": 5},
    ])

    loot = [{"name": "Short Sword", "value": 10}, {"name": "5 gp", "value": 5}]
    result = end_combat(sid, loot=loot)
    assert result["loot"] == loot


def test_end_combat_no_active(game_db):
    sid, _, _ = _setup_combat_session(game_db)
    result = end_combat(sid)
    assert "error" in result
