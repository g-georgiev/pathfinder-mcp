"""Character persistence tools — create, read, list characters."""

import json
import re
import uuid

from game_state import get_game_db
from compute.derived import compute_derived_stats


def _slugify(name: str) -> str:
    """Convert a name to a URL-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def persist_character(
    session_id: str,
    player_id: str,
    character_data: dict,
) -> dict:
    """Create and persist a new character in the game state database.

    Validates the session exists, generates a unique character ID from the
    slugified name + short UUID, computes derived stats, and inserts the
    character into the database.

    Args:
        session_id: The session this character belongs to
        player_id: The player who owns this character (empty string for NPCs)
        character_data: Full character data dict containing:
            name, race, classes, abilities, feats, traits, skills,
            equipment, hp_breakdown, spells_known, spells_prepared, etc.

    Returns:
        dict with character_id, name, level, classes, and computed stats,
        or {"error": "..."} on failure.
    """
    db = get_game_db()
    try:
        # Validate session exists
        session = db.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not session:
            return {"error": f"Session '{session_id}' not found"}

        # Validate player exists if provided
        if player_id:
            player = db.execute(
                "SELECT id FROM players WHERE id = ? AND session_id = ?",
                (player_id, session_id),
            ).fetchone()
            if not player:
                return {"error": f"Player '{player_id}' not found in session '{session_id}'"}

        # Generate character ID
        name = character_data.get("name", "Unknown")
        slug = _slugify(name)
        char_id = f"{slug}-{uuid.uuid4().hex[:8]}"

        # Compute total level
        classes = character_data.get("classes", [])
        total_level = sum(c.get("level", 1) for c in classes)
        classes_str = ", ".join(
            f"{c.get('name', '?')} {c.get('level', 1)}" for c in classes
        )
        race = character_data.get("race", "")

        # Compute derived stats
        computed = compute_derived_stats(character_data)

        # Set max_hp from computed
        max_hp = computed.get("hp", {}).get("max", 0)

        # Store character
        data_json = json.dumps(character_data)
        computed_json = json.dumps(computed)

        db.execute(
            """INSERT INTO characters
               (id, session_id, player_id, name, level, classes, race,
                is_npc, status, current_hp, max_hp, data, computed)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'alive', ?, ?, ?, ?)""",
            (
                char_id, session_id,
                player_id if player_id else None,
                name, total_level, classes_str, race,
                max_hp, max_hp, data_json, computed_json,
            ),
        )
        db.commit()

        return {
            "character_id": char_id,
            "name": name,
            "level": total_level,
            "classes": classes_str,
            "computed": computed,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def get_character(session_id: str, character_id: str) -> dict:
    """Retrieve a character's full data, computed stats, and active conditions.

    Args:
        session_id: The session the character belongs to
        character_id: The character's unique identifier

    Returns:
        dict with character data, computed stats, and conditions list,
        or {"error": "..."} if not found.
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found in session '{session_id}'"}

        result = dict(row)
        result["data"] = json.loads(result.get("data", "{}"))
        result["computed"] = json.loads(result.get("computed", "{}"))

        # Get active conditions
        conditions = db.execute(
            "SELECT * FROM conditions WHERE character_id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchall()
        result["conditions"] = [dict(c) for c in conditions]

        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def list_characters(session_id: str) -> list[dict]:
    """List all player characters in a session with summary info.

    Args:
        session_id: The session to list characters for

    Returns:
        List of dicts with id, name, level, classes, race, current_hp,
        max_hp, and status for each character.
    """
    db = get_game_db()
    try:
        rows = db.execute(
            """SELECT id, name, level, classes, race, current_hp, max_hp, status
               FROM characters
               WHERE session_id = ? AND is_npc = 0
               ORDER BY name""",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()
