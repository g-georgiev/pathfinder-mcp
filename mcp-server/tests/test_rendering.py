"""Tests for character rendering (markdown export/import)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.character import persist_character, get_character
from tools.rendering import render_character_md, import_character_md


def _create_session(game_db):
    """Helper: create a test session."""
    game_db.execute(
        "INSERT INTO sessions (id, name) VALUES ('test-session', 'Test Game')"
    )
    game_db.commit()


class TestRenderCharacterMd:
    def test_renders_valid_markdown(self, game_db, sample_character_data):
        _create_session(game_db)

        created = persist_character("test-session", "", sample_character_data)
        char_id = created["character_id"]

        md = render_character_md("test-session", char_id)
        assert isinstance(md, str)
        assert len(md) > 100

        # Check frontmatter
        assert md.startswith("---")
        assert "name: Test Fighter" in md
        assert "race: Human" in md

        # Check key sections
        assert "## Ability Scores" in md
        assert "## Combat Stats" in md
        assert "### Armor Class" in md
        assert "### Hit Points" in md
        assert "### Saving Throws" in md
        assert "### Offense" in md

        # Check ability scores appear
        assert "| STR | 18 |" in md
        assert "| DEX | 14 |" in md

        # Check BAB
        assert "+5" in md

        # Check equipment
        assert "## Equipment" in md
        assert "Longsword +1" in md
        assert "Full Plate" in md

        # Check feats
        assert "## Feats" in md
        assert "Power Attack" in md

    def test_renders_wizard_with_spells(self, game_db, sample_wizard_data):
        _create_session(game_db)

        created = persist_character("test-session", "", sample_wizard_data)
        char_id = created["character_id"]

        md = render_character_md("test-session", char_id)
        assert "## Spellcasting" in md
        assert "wizard" in md.lower()

    def test_render_nonexistent(self, game_db):
        _create_session(game_db)
        result = render_character_md("test-session", "fake-id")
        assert isinstance(result, dict)
        assert "error" in result


class TestImportCharacterMd:
    def test_import_basic(self, game_db):
        """Import a minimal markdown character."""
        _create_session(game_db)

        md = """---
name: Imported Hero
level: 3
classes: Fighter 3
race: Elf
alignment: "chaotic good"
---

# Imported Hero
**Level 3 Elf Fighter 3**

## Ability Scores

| Ability | Score | Mod |
|---------|-------|-----|
| STR | 16 | +3 |
| DEX | 14 | +2 |
| CON | 12 | +1 |
| INT | 10 | +0 |
| WIS | 10 | +0 |
| CHA | 8 | -1 |

## Feats

| Level | Feat | Notes |
|-------|------|-------|
| 1 | Power Attack | Trade AB for damage |
| 1 | Cleave | Bonus fighter feat |
| 2 | Weapon Focus | Longsword |

## Traits

| Trait | Effect |
|-------|--------|
| Reactionary | +2 trait bonus on initiative checks |

## Skills

| Skill | Total | Ranks |
|-------|-------|-------|
| Perception | +3 | 3 |
| Climb | +9 | 3 |

## Equipment

- **Longsword** (weapon)
- **Chain Shirt** (armor)
- **Wooden Shield** (offhand)

**Gold**: 150 gp
"""
        result = import_character_md("test-session", "", md)
        assert "error" not in result
        assert "character_id" in result
        assert isinstance(result.get("warnings"), list)

        # Verify the character was persisted
        char = get_character("test-session", result["character_id"])
        assert char["name"] == "Imported Hero"
        data = char["data"]
        assert data["race"] == "Elf"
        assert data["abilities"]["str"] == 16
        assert data["gold"] == 150

    def test_round_trip(self, game_db, sample_character_data):
        """Render a character to MD then import it — key fields should survive."""
        _create_session(game_db)

        created = persist_character("test-session", "", sample_character_data)
        char_id = created["character_id"]

        # Render to markdown
        md = render_character_md("test-session", char_id)
        assert isinstance(md, str)

        # Import the markdown
        imported = import_character_md("test-session", "", md)
        assert "error" not in imported
        assert "character_id" in imported

        # Compare key fields
        original = get_character("test-session", char_id)
        reimported = get_character("test-session", imported["character_id"])

        assert reimported["name"] == original["name"]
        assert reimported["data"]["race"] == original["data"]["race"]
        # Ability scores should survive the round trip
        for ab in ("str", "dex", "con", "int", "wis", "cha"):
            assert reimported["data"]["abilities"][ab] == original["data"]["abilities"][ab]

    def test_import_missing_frontmatter(self, game_db):
        _create_session(game_db)

        md = """# No Frontmatter Character

## Ability Scores

| Ability | Score | Mod |
|---------|-------|-----|
| STR | 10 | +0 |
| DEX | 10 | +0 |
| CON | 10 | +0 |
| INT | 10 | +0 |
| WIS | 10 | +0 |
| CHA | 10 | +0 |
"""
        result = import_character_md("test-session", "", md)
        assert "error" not in result
        assert any("frontmatter" in w.lower() for w in result.get("warnings", []))
