"""Tests for character persistence tools."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.character import persist_character, get_character, list_characters


class TestPersistCharacter:
    def test_persist_and_retrieve(self, game_db, sample_character_data):
        """Create a character and retrieve it."""
        # Create a session first
        game_db.execute(
            "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
        )
        game_db.commit()

        result = persist_character("test-session", "", sample_character_data)
        assert "error" not in result
        assert "character_id" in result
        assert result["name"] == "Test Fighter"
        assert result["level"] == 5
        assert "computed" in result
        assert result["computed"]["bab"] == 5

    def test_persist_requires_valid_session(self, game_db, sample_character_data):
        """Should error if session doesn't exist."""
        result = persist_character("nonexistent", "", sample_character_data)
        assert "error" in result

    def test_persist_validates_player(self, game_db, sample_character_data):
        """Should error if player doesn't exist in session."""
        game_db.execute(
            "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
        )
        game_db.commit()

        result = persist_character("test-session", "fake-player", sample_character_data)
        assert "error" in result


class TestGetCharacter:
    def test_get_full_character(self, game_db, sample_character_data):
        game_db.execute(
            "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
        )
        game_db.commit()

        created = persist_character("test-session", "", sample_character_data)
        char_id = created["character_id"]

        result = get_character("test-session", char_id)
        assert "error" not in result
        assert result["name"] == "Test Fighter"
        assert isinstance(result["data"], dict)
        assert isinstance(result["computed"], dict)
        assert "conditions" in result

    def test_get_nonexistent(self, game_db):
        game_db.execute(
            "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
        )
        game_db.commit()

        result = get_character("test-session", "nonexistent-id")
        assert "error" in result


class TestListCharacters:
    def test_list_characters(self, game_db, sample_character_data, sample_wizard_data):
        game_db.execute(
            "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
        )
        game_db.commit()

        persist_character("test-session", "", sample_character_data)
        persist_character("test-session", "", sample_wizard_data)

        result = list_characters("test-session")
        assert len(result) == 2
        names = {r["name"] for r in result}
        assert "Test Fighter" in names
        assert "Test Wizard" in names

    def test_list_empty_session(self, game_db):
        game_db.execute(
            "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
        )
        game_db.commit()

        result = list_characters("test-session")
        assert result == []
