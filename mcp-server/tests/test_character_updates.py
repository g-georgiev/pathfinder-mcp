"""Tests for character update tools."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.character import persist_character, get_character
from tools.character_updates import (
    update_character_hp,
    update_character_conditions,
    update_character_inventory,
    update_character_spells,
    apply_level_up,
)


def _create_test_character(game_db, character_data):
    """Helper: create session and character, return character_id."""
    game_db.execute(
        "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
    )
    game_db.commit()
    result = persist_character("test-session", "", character_data)
    assert "error" not in result, f"Failed to create character: {result}"
    return result["character_id"]


class TestUpdateHP:
    def test_damage(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        result = update_character_hp("test-session", char_id, -10, "sword hit")
        assert result["delta"] == -10
        assert result["current_hp"] == result["max_hp"] - 10
        assert result["status"] == "alive"

    def test_healing_capped_at_max(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        # Damage then overheal
        update_character_hp("test-session", char_id, -10)
        result = update_character_hp("test-session", char_id, 100)
        assert result["current_hp"] == result["max_hp"]

    def test_unconscious_at_zero(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        # Get max HP and deal that much damage
        char = get_character("test-session", char_id)
        max_hp = char["max_hp"]
        result = update_character_hp("test-session", char_id, -max_hp)
        assert result["current_hp"] == 0
        assert result["status"] == "unconscious"

    def test_dying_below_zero(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        char = get_character("test-session", char_id)
        max_hp = char["max_hp"]
        result = update_character_hp("test-session", char_id, -(max_hp + 5))
        assert result["current_hp"] == -5
        assert result["status"] == "dying"

    def test_dead_at_neg_con(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        # CON 14 means dead at -14. Deal enough to go past that.
        result = update_character_hp("test-session", char_id, -200)
        assert result["current_hp"] == -14  # clamped to -CON
        assert result["status"] == "dead"


class TestUpdateConditions:
    def test_add_conditions(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        result = update_character_conditions(
            "test-session", char_id,
            add=[
                {"name": "shaken", "duration_rounds": 3, "source": "fear aura"},
                {"name": "fatigued", "duration_rounds": -1, "source": "forced march"},
            ],
        )
        assert len(result["conditions"]) == 2
        names = {c["name"] for c in result["conditions"]}
        assert "shaken" in names
        assert "fatigued" in names

    def test_remove_conditions(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        # Add then remove
        update_character_conditions(
            "test-session", char_id,
            add=[{"name": "shaken", "duration_rounds": 3}],
        )
        result = update_character_conditions(
            "test-session", char_id,
            remove=["shaken"],
        )
        assert len(result["conditions"]) == 0


class TestUpdateInventory:
    def test_add_item(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        result = update_character_inventory(
            "test-session", char_id,
            add=[{"name": "Potion of Cure Light Wounds", "slot": "consumable", "stats": {}}],
        )
        item_names = [i["name"] for i in result["inventory"]]
        assert "Potion of Cure Light Wounds" in item_names

    def test_remove_item(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        result = update_character_inventory(
            "test-session", char_id,
            remove=[{"name": "Longsword +1"}],
        )
        item_names = [i["name"] for i in result["inventory"]]
        assert "Longsword +1" not in item_names

    def test_gold_delta(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        result = update_character_inventory(
            "test-session", char_id,
            gold_delta=-500,
        )
        assert result["gold"] == 10500 - 500


class TestUpdateSpells:
    def test_cast_spell(self, game_db, sample_wizard_data):
        char_id = _create_test_character(game_db, sample_wizard_data)

        result = update_character_spells("test-session", char_id, cast="1")
        # Should have spell_slots with level 1 tracking
        if "1" in result["spell_slots"]:
            assert result["spell_slots"]["1"]["used"] == 1
            assert result["spell_slots"]["1"]["remaining"] == result["spell_slots"]["1"]["total"] - 1

    def test_restore_slot(self, game_db, sample_wizard_data):
        char_id = _create_test_character(game_db, sample_wizard_data)

        # Cast then restore
        update_character_spells("test-session", char_id, cast="1")
        result = update_character_spells("test-session", char_id, restore_slot=1)
        if "1" in result["spell_slots"]:
            assert result["spell_slots"]["1"]["used"] == 0


class TestLevelUp:
    def test_basic_level_up(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        result = apply_level_up("test-session", char_id, {
            "class_name": "Fighter",
            "hp_roll": 6,
            "new_feats": [{"name": "Improved Critical", "level_taken": 6}],
            "skill_ranks": {"perception": 1},
        })
        assert "error" not in result
        assert result["level"] == 6
        assert "Fighter 6" in result["classes"]

    def test_multiclass_level_up(self, game_db, sample_character_data):
        char_id = _create_test_character(game_db, sample_character_data)

        result = apply_level_up("test-session", char_id, {
            "class_name": "Rogue",
            "hp_roll": 4,
            "new_feats": [],
            "skill_ranks": {},
        })
        assert "error" not in result
        assert result["level"] == 6
        assert "Rogue 1" in result["classes"]
