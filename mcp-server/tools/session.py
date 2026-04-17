"""Session lifecycle tools — create, join, list, save/load sessions."""

import json
import uuid

from game_state import get_game_db


def create_session(
    name: str,
    tone: str = "heroic",
    setting: str = "",
    dm_notes: str = "",
) -> dict:
    """Create a new game session.

    Args:
        name: Display name for the session (e.g. "Rise of the Runelords")
        tone: Narrative tone — heroic, gritty, comedic, etc.
        setting: Optional world or campaign setting description
        dm_notes: Private DM notes about this session
    """
    session_id = uuid.uuid4().hex[:12]
    db = get_game_db()
    try:
        db.execute(
            "INSERT INTO sessions (id, name, tone, setting, dm_notes) VALUES (?, ?, ?, ?, ?)",
            (session_id, name, tone, setting, dm_notes),
        )
        db.commit()
        row = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return {
            "session_id": row["id"],
            "name": row["name"],
            "tone": row["tone"],
            "created_at": row["created_at"],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def get_session(session_id: str) -> dict:
    """Get session metadata and its current players.

    Args:
        session_id: The session identifier
    """
    db = get_game_db()
    try:
        row = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return {"error": f"Session '{session_id}' not found"}
        result = dict(row)
        players = db.execute(
            "SELECT * FROM players WHERE session_id = ?", (session_id,)
        ).fetchall()
        result["players"] = [dict(p) for p in players]
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def list_sessions() -> list[dict]:
    """List all sessions with basic metadata."""
    db = get_game_db()
    try:
        rows = db.execute(
            "SELECT id, name, tone, status, created_at FROM sessions ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def join_session(
    session_id: str,
    player_id: str,
    player_name: str,
) -> dict:
    """Add a player to a session.

    Args:
        session_id: The session to join
        player_id: Unique identifier for the player
        player_name: Display name for the player
    """
    db = get_game_db()
    try:
        db.execute(
            "INSERT INTO players (id, session_id, name) VALUES (?, ?, ?)",
            (player_id, session_id, player_name),
        )
        db.commit()
        row = db.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
        return {
            "player_id": row["id"],
            "session_id": row["session_id"],
            "player_name": row["name"],
            "joined_at": row["joined_at"],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def save_session(session_id: str) -> dict:
    """Snapshot all session data for later restore.

    Serializes players, characters, conditions, combats, events, quests,
    and foreshadow threads into a single JSON blob stored in the snapshots table.

    Args:
        session_id: The session to snapshot
    """
    db = get_game_db()
    try:
        session = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not session:
            return {"error": f"Session '{session_id}' not found"}

        tables = ["players", "characters", "conditions", "combats", "events", "quests", "foreshadow"]
        snapshot = {}
        for table in tables:
            rows = db.execute(
                f"SELECT * FROM {table} WHERE session_id = ?", (session_id,)
            ).fetchall()
            snapshot[table] = [dict(r) for r in rows]

        snapshot_json = json.dumps(snapshot)
        db.execute(
            "INSERT INTO snapshots (session_id, snapshot_data) VALUES (?, ?)",
            (session_id, snapshot_json),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM snapshots WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        return {
            "snapshot_id": row["id"],
            "session_id": row["session_id"],
            "created_at": row["created_at"],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def load_session(session_id: str) -> dict:
    """Restore session state from the most recent snapshot.

    Deletes current data for the session (conditions, combats, events, quests,
    foreshadow, characters, players) and re-inserts from the snapshot within
    a transaction.

    Args:
        session_id: The session to restore
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM snapshots WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if not row:
            return {"error": f"No snapshots found for session '{session_id}'"}

        snapshot_id = row["id"]
        snapshot_created = row["created_at"]
        snapshot = json.loads(row["snapshot_data"])

        # Delete order respects foreign keys (children first)
        delete_order = ["conditions", "combats", "events", "quests", "foreshadow", "characters", "players"]
        for table in delete_order:
            db.execute(f"DELETE FROM {table} WHERE session_id = ?", (session_id,))

        # Re-insert from snapshot
        for table in ["players", "characters", "conditions", "combats", "events", "quests", "foreshadow"]:
            rows = snapshot.get(table, [])
            if not rows:
                continue
            columns = list(rows[0].keys())
            placeholders = ", ".join("?" for _ in columns)
            col_names = ", ".join(columns)
            for r in rows:
                vals = [r[c] for c in columns]
                db.execute(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})", vals)

        db.commit()
        return {
            "session_id": session_id,
            "restored_from_snapshot_id": snapshot_id,
            "created_at": snapshot_created,
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
