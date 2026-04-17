"""Tests for NPC management tools."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.npc import persist_npc, get_npc, list_npcs, update_npc


def _create_session(game_db):
    """Helper: create a test session."""
    game_db.execute(
        "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
    )
    game_db.commit()


class TestPersistNPC:
    def test_sparse_stat_block(self, game_db):
        """NPC with just name/hp/ac — no class lookup needed."""
        _create_session(game_db)

        result = persist_npc("test-session", {
            "name": "Goblin Warrior",
            "hp": 6,
            "ac": 16,
            "touch_ac": 13,
            "flat_footed_ac": 14,
            "bab": 1,
            "fort": 3,
            "ref": 1,
            "will": -1,
            "role": "enemy",
            "location": "Goblin Cave",
            "disposition": "hostile",
        })
        assert "error" not in result
        assert "npc_id" in result
        assert result["name"] == "Goblin Warrior"
        assert result["computed"]["hp"]["max"] == 6
        assert result["computed"]["ac"]["total"] == 16

    def test_full_class_npc(self, game_db, sample_character_data):
        """NPC with full class data — runs through compute engine."""
        _create_session(game_db)

        npc_data = dict(sample_character_data)
        npc_data["name"] = "NPC Fighter"
        npc_data["role"] = "ally"
        npc_data["disposition"] = "friendly"
        npc_data["location"] = "Tavern"

        result = persist_npc("test-session", npc_data)
        assert "error" not in result
        assert result["computed"]["bab"] == 5

    def test_persist_requires_valid_session(self, game_db):
        result = persist_npc("nonexistent", {"name": "Goblin"})
        assert "error" in result


class TestGetNPC:
    def test_get_npc(self, game_db):
        _create_session(game_db)

        created = persist_npc("test-session", {
            "name": "Bartender",
            "hp": 8,
            "ac": 10,
            "role": "noncombatant",
            "notes": "Knows rumors about the dungeon.",
        })
        npc_id = created["npc_id"]

        result = get_npc("test-session", npc_id)
        assert "error" not in result
        assert result["name"] == "Bartender"
        assert isinstance(result["data"], dict)
        assert isinstance(result["computed"], dict)

    def test_get_nonexistent(self, game_db):
        _create_session(game_db)
        result = get_npc("test-session", "fake-npc-id")
        assert "error" in result


class TestListNPCs:
    def test_list_all(self, game_db):
        _create_session(game_db)

        persist_npc("test-session", {"name": "Goblin 1", "hp": 5, "role": "enemy", "location": "Cave"})
        persist_npc("test-session", {"name": "Goblin 2", "hp": 5, "role": "enemy", "location": "Cave"})
        persist_npc("test-session", {"name": "Merchant", "hp": 8, "role": "noncombatant", "location": "Town"})

        result = list_npcs("test-session")
        assert len(result) == 3

    def test_filter_by_role(self, game_db):
        _create_session(game_db)

        persist_npc("test-session", {"name": "Goblin", "hp": 5, "role": "enemy", "location": "Cave"})
        persist_npc("test-session", {"name": "Merchant", "hp": 8, "role": "noncombatant", "location": "Town"})

        result = list_npcs("test-session", role="enemy")
        assert len(result) == 1
        assert result[0]["name"] == "Goblin"

    def test_filter_by_location(self, game_db):
        _create_session(game_db)

        persist_npc("test-session", {"name": "Goblin", "hp": 5, "role": "enemy", "location": "Cave"})
        persist_npc("test-session", {"name": "Merchant", "hp": 8, "role": "noncombatant", "location": "Town"})

        result = list_npcs("test-session", location="Town")
        assert len(result) == 1
        assert result[0]["name"] == "Merchant"

    def test_filter_by_status(self, game_db):
        _create_session(game_db)

        created = persist_npc("test-session", {"name": "Dead Goblin", "hp": 5, "role": "enemy"})
        update_npc("test-session", created["npc_id"], {"status": "dead", "current_hp": 0})
        persist_npc("test-session", {"name": "Live Goblin", "hp": 5, "role": "enemy"})

        alive = list_npcs("test-session", status="alive")
        assert len(alive) == 1
        assert alive[0]["name"] == "Live Goblin"

        all_npcs = list_npcs("test-session", status="")
        assert len(all_npcs) == 2


class TestUpdateNPC:
    def test_update_disposition(self, game_db):
        _create_session(game_db)

        created = persist_npc("test-session", {
            "name": "Merchant",
            "hp": 8,
            "disposition": "neutral",
        })
        npc_id = created["npc_id"]

        result = update_npc("test-session", npc_id, {"disposition": "friendly"})
        assert result["data"]["disposition"] == "friendly"

    def test_update_hp_and_status(self, game_db):
        _create_session(game_db)

        created = persist_npc("test-session", {"name": "Goblin", "hp": 5})
        npc_id = created["npc_id"]

        result = update_npc("test-session", npc_id, {
            "current_hp": 0,
            "status": "dead",
        })
        assert result["current_hp"] == 0
        assert result["status"] == "dead"

    def test_update_nonexistent(self, game_db):
        _create_session(game_db)
        result = update_npc("test-session", "fake-id", {"notes": "test"})
        assert "error" in result
