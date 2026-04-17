"""NPC management tools — create, read, list, update NPCs.

NPCs are stored in the same characters table with is_npc=1 and player_id=NULL.
They support both full class-based stat blocks (run through compute_derived_stats)
and sparse stat blocks (name/hp/ac/attack copied directly to computed).
"""

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


def persist_npc(session_id: str, npc_data: dict) -> dict:
    """Create and persist a new NPC in the game state database.

    Supports two modes:
    1. Full class data: if npc_data has "classes" with class entries and
       "abilities", runs compute_derived_stats for a full stat block.
    2. Sparse stat block: if npc_data has direct stats (hp, ac, attack),
       copies them directly to the computed column without class lookups.

    NPC-specific fields (role, disposition, location, notes) are stored
    in the data blob.

    Args:
        session_id: The session this NPC belongs to
        npc_data: NPC data dict. Required: name. Optional:
            classes, abilities, feats, equipment (full mode), or
            hp, ac, attack, saves (sparse mode), plus
            role, disposition, location, notes.

    Returns:
        dict with npc_id, name, level, computed stats.
    """
    db = get_game_db()
    try:
        # Validate session
        session = db.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not session:
            return {"error": f"Session '{session_id}' not found"}

        name = npc_data.get("name", "Unknown NPC")
        slug = _slugify(name)
        npc_id = f"npc-{slug}-{uuid.uuid4().hex[:8]}"

        # Determine if full or sparse stat block
        has_classes = bool(npc_data.get("classes"))
        has_abilities = bool(npc_data.get("abilities"))

        if has_classes and has_abilities:
            # Full mode: compute derived stats
            computed = compute_derived_stats(npc_data)
            classes = npc_data.get("classes", [])
            total_level = sum(c.get("level", 1) for c in classes)
            classes_str = ", ".join(
                f"{c.get('name', '?')} {c.get('level', 1)}" for c in classes
            )
        else:
            # Sparse mode: copy direct stats to computed
            computed = {
                "hp": {"max": npc_data.get("hp", 0), "breakdown": {}},
                "ac": {
                    "total": npc_data.get("ac", 10),
                    "touch": npc_data.get("touch_ac", 10),
                    "flat_footed": npc_data.get("flat_footed_ac", 10),
                    "components": {},
                },
                "saves": {
                    "fort": npc_data.get("fort", 0),
                    "ref": npc_data.get("ref", 0),
                    "will": npc_data.get("will", 0),
                },
                "bab": npc_data.get("bab", 0),
                "attacks": npc_data.get("attacks", []),
                "initiative": {"total": npc_data.get("initiative", 0), "components": {}},
                "cmb_cmd": {
                    "cmb": npc_data.get("cmb", 0),
                    "cmd": npc_data.get("cmd", 10),
                },
                "skills": npc_data.get("skills", {}),
                "spell_slots": npc_data.get("spell_slots", {}),
                "ability_mods": npc_data.get("ability_mods", {}),
            }
            total_level = npc_data.get("level", 1)
            classes_str = npc_data.get("cr", npc_data.get("type", "NPC"))

        max_hp = computed.get("hp", {}).get("max", 0)
        race = npc_data.get("race", "")
        status = npc_data.get("status", "alive")

        # Store NPC-specific fields in data blob
        data = dict(npc_data)
        data["role"] = npc_data.get("role", "")
        data["disposition"] = npc_data.get("disposition", "neutral")
        data["location"] = npc_data.get("location", "")
        data["notes"] = npc_data.get("notes", "")

        db.execute(
            """INSERT INTO characters
               (id, session_id, player_id, name, level, classes, race,
                is_npc, status, current_hp, max_hp, data, computed)
               VALUES (?, ?, NULL, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)""",
            (
                npc_id, session_id, name, total_level, classes_str, race,
                status, max_hp, max_hp,
                json.dumps(data), json.dumps(computed),
            ),
        )
        db.commit()

        return {
            "npc_id": npc_id,
            "name": name,
            "level": total_level,
            "classes": classes_str,
            "computed": computed,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def get_npc(session_id: str, npc_id: str) -> dict:
    """Retrieve an NPC's full data and computed stats.

    Args:
        session_id: The session the NPC belongs to
        npc_id: The NPC's unique identifier

    Returns:
        dict with NPC data, computed stats, and conditions,
        or {"error": "..."} if not found.
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ? AND is_npc = 1",
            (npc_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"NPC '{npc_id}' not found in session '{session_id}'"}

        result = dict(row)
        result["data"] = json.loads(result.get("data", "{}"))
        result["computed"] = json.loads(result.get("computed", "{}"))

        # Get active conditions
        conditions = db.execute(
            "SELECT * FROM conditions WHERE character_id = ? AND session_id = ?",
            (npc_id, session_id),
        ).fetchall()
        result["conditions"] = [dict(c) for c in conditions]

        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def list_npcs(
    session_id: str,
    role: str = "",
    location: str = "",
    status: str = "alive",
) -> list[dict]:
    """List NPCs in a session with optional filters.

    Args:
        session_id: The session to list NPCs for
        role: Filter by NPC role (substring match in data JSON)
        location: Filter by NPC location (substring match in data JSON)
        status: Filter by status (default: "alive", use "" for all)

    Returns:
        List of NPC summary dicts.
    """
    db = get_game_db()
    try:
        conditions = ["session_id = ?", "is_npc = 1"]
        params: list = [session_id]

        if status:
            conditions.append("status = ?")
            params.append(status)

        where = " AND ".join(conditions)
        rows = db.execute(
            f"SELECT id, name, level, classes, race, current_hp, max_hp, status, data "
            f"FROM characters WHERE {where} ORDER BY name",
            params,
        ).fetchall()

        results = []
        for r in rows:
            row_dict = dict(r)
            data = json.loads(row_dict.pop("data", "{}"))

            # Apply role/location filters on the data blob
            if role and role.lower() not in data.get("role", "").lower():
                continue
            if location and location.lower() not in data.get("location", "").lower():
                continue

            row_dict["role"] = data.get("role", "")
            row_dict["disposition"] = data.get("disposition", "neutral")
            row_dict["location"] = data.get("location", "")
            results.append(row_dict)

        return results
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def update_npc(session_id: str, npc_id: str, updates: dict) -> dict:
    """Update an NPC's data by merging in new values.

    Merges the updates dict into the NPC's data JSON. If HP or status
    changes are included, also updates the indexed columns.

    Args:
        session_id: The session the NPC belongs to
        npc_id: The NPC's unique identifier
        updates: Dict of fields to update (merged into data blob).
            Special keys: "current_hp", "status", "hp" (max), "disposition",
            "role", "location", "notes".

    Returns:
        Updated NPC dict.
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ? AND is_npc = 1",
            (npc_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"NPC '{npc_id}' not found"}

        data = json.loads(row["data"] or "{}")
        computed = json.loads(row["computed"] or "{}")

        # Merge updates into data blob
        for key, value in updates.items():
            data[key] = value

        # Handle indexed column updates
        current_hp = row["current_hp"]
        max_hp = row["max_hp"]
        status = row["status"]

        if "current_hp" in updates:
            current_hp = updates["current_hp"]
        if "hp" in updates:
            max_hp = updates["hp"]
            computed.setdefault("hp", {})["max"] = max_hp
        if "status" in updates:
            status = updates["status"]

        db.execute(
            """UPDATE characters
               SET data = ?, computed = ?, current_hp = ?, max_hp = ?,
                   status = ?, updated_at = datetime('now')
               WHERE id = ? AND session_id = ?""",
            (
                json.dumps(data), json.dumps(computed),
                current_hp, max_hp, status,
                npc_id, session_id,
            ),
        )
        db.commit()

        return {
            "npc_id": npc_id,
            "name": data.get("name", ""),
            "current_hp": current_hp,
            "max_hp": max_hp,
            "status": status,
            "data": data,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
