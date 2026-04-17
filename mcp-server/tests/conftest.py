"""Shared test fixtures for MCP expansion tests."""

import sqlite3
from pathlib import Path

import pytest

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RULES_DB_PATH = str(PROJECT_ROOT / "db" / "pathfinder.db")


@pytest.fixture
def rules_db():
    """Read-only connection to the real pathfinder.db rules database."""
    conn = sqlite3.connect(RULES_DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def game_db(tmp_path, monkeypatch):
    """Fresh game_state.db in a temp directory, patched into game_state module."""
    import game_state

    db_path = str(tmp_path / "game_state.db")
    monkeypatch.setattr(game_state, "GAME_STATE_DB_PATH", db_path)
    monkeypatch.setattr(game_state, "_initialized", False)
    conn = game_state.get_game_db()
    yield conn
    conn.close()


@pytest.fixture
def sample_character_data():
    """Minimal valid character data matching persist_character input schema.

    Based on a simplified Level 5 Human Fighter for predictable test values.
    """
    return {
        "name": "Test Fighter",
        "race": "Human",
        "classes": [{"name": "Fighter", "archetype": None, "level": 5}],
        "abilities": {
            "str": 18, "dex": 14, "con": 14,
            "int": 10, "wis": 12, "cha": 8,
        },
        "feats": [
            {"name": "Power Attack", "level_taken": 1},
            {"name": "Weapon Focus", "level_taken": 1},
            {"name": "Toughness", "level_taken": 2},
            {"name": "Weapon Specialization", "level_taken": 4},
        ],
        "traits": [
            {"name": "Reactionary", "effect": "+2 trait bonus on initiative checks"},
        ],
        "skills": {
            "perception": 5,
            "climb": 3,
            "swim": 2,
        },
        "equipment": [
            {
                "name": "Longsword +1",
                "slot": "weapon",
                "stats": {
                    "type": "melee",
                    "damage": "1d8",
                    "crit": "19-20/x2",
                    "enhancement": 1,
                    "ability": "str",
                    "category": "martial",
                },
            },
            {
                "name": "Full Plate",
                "slot": "armor",
                "stats": {
                    "ac_bonus": 9,
                    "max_dex": 1,
                    "type": "armor",
                },
            },
            {
                "name": "Heavy Steel Shield",
                "slot": "offhand",
                "stats": {
                    "ac_bonus": 2,
                    "type": "shield",
                },
            },
        ],
        "spells_known": {},
        "spells_prepared": {},
        "class_features": [],
        "racial_traits": [
            {"name": "Bonus Feat", "effect": "Extra feat at 1st level"},
            {"name": "Skilled", "effect": "Extra skill rank per level"},
        ],
        "hp_breakdown": {
            "hit_dice": 33,  # 10 (max L1) + 23 (avg 5.5×4 rounded up = 6×4=24, but let's use 23 for non-round)
            "con": 10,       # +2 CON × 5 levels
            "favored_class": 5,
            "toughness": 5,
            "misc": 0,
        },
        "gold": 10500,
        "notes": "Test character for unit tests.",
    }


@pytest.fixture
def sample_wizard_data():
    """Level 10 Wizard for spellcasting tests."""
    return {
        "name": "Test Wizard",
        "race": "Human",
        "classes": [{"name": "Wizard", "archetype": None, "level": 10}],
        "abilities": {
            "str": 10, "dex": 14, "con": 14,
            "int": 24, "wis": 12, "cha": 8,
        },
        "feats": [
            {"name": "Scribe Scroll", "level_taken": 1},
            {"name": "Improved Initiative", "level_taken": 1},
            {"name": "Spell Focus", "level_taken": 3},
        ],
        "traits": [],
        "skills": {"spellcraft": 10, "knowledge (arcana)": 10},
        "equipment": [],
        "spells_known": {
            "0": ["detect magic", "read magic", "prestidigitation", "light"],
            "1": ["magic missile", "mage armor", "shield", "grease"],
            "2": ["glitterdust", "invisibility", "mirror image"],
            "3": ["fireball", "haste", "dispel magic"],
            "4": ["dimension door", "black tentacles"],
            "5": ["teleport", "wall of force"],
        },
        "spells_prepared": {},
        "class_features": [],
        "racial_traits": [],
        "hp_breakdown": {
            "hit_dice": 37,  # 6 + (4×9)
            "con": 20,       # +2 × 10
            "favored_class": 0,
            "toughness": 0,
            "misc": 0,
        },
        "gold": 62000,
        "notes": "Test wizard for spellcasting tests.",
    }
