"""Campaign memory tools — events, quests, foreshadowing threads."""

import json

from game_state import get_game_db


def log_event(
    session_id: str,
    event_type: str,
    summary: str,
    participants: list[str] = [],
    location: str = "",
    significance: str = "minor",
) -> dict:
    """Log a campaign event to the session history.

    Args:
        session_id: The session this event belongs to
        event_type: Category of event (combat, roleplay, discovery, travel, quest, etc.)
        summary: What happened — written for future recall by the DM
        participants: List of character/NPC names involved
        location: Where the event took place
        significance: How important — minor, moderate, major, critical
    """
    db = get_game_db()
    try:
        participants_json = json.dumps(participants)
        db.execute(
            "INSERT INTO events (session_id, event_type, summary, participants, location, significance) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, event_type, summary, participants_json, location, significance),
        )
        db.commit()
        # Rebuild FTS index
        db.execute("INSERT INTO fts_events(fts_events) VALUES('rebuild')")
        db.commit()
        row = db.execute(
            "SELECT * FROM events WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        return {
            "event_id": row["id"],
            "session_id": row["session_id"],
            "event_type": row["event_type"],
            "summary": row["summary"],
            "timestamp": row["timestamp"],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def recall_events(
    session_id: str,
    query: str = "",
    event_type: str = "",
    participant: str = "",
    last_n: int = 20,
    significance: str = "",
) -> list[dict]:
    """Search session event history with optional full-text search.

    Args:
        session_id: The session to search
        query: Full-text search query (searches event summaries via FTS5)
        event_type: Filter by event type
        participant: Filter by participant name (substring match in JSON array)
        last_n: Maximum number of events to return (default 20)
        significance: Filter by significance level
    """
    db = get_game_db()
    try:
        if query:
            # FTS5 search joined back to events table
            conditions = ["e.session_id = ?"]
            params: list = [session_id]

            sql = (
                "SELECT e.* FROM events e "
                "INNER JOIN fts_events f ON e.id = f.rowid "
                "WHERE f.fts_events MATCH ? AND e.session_id = ?"
            )
            params_fts: list = [query, session_id]

            if event_type:
                sql += " AND e.event_type = ?"
                params_fts.append(event_type)
            if participant:
                sql += " AND e.participants LIKE ?"
                params_fts.append(f"%{participant}%")
            if significance:
                sql += " AND e.significance = ?"
                params_fts.append(significance)

            sql += " ORDER BY e.timestamp DESC LIMIT ?"
            params_fts.append(last_n)

            rows = db.execute(sql, params_fts).fetchall()
        else:
            conditions = ["session_id = ?"]
            params_plain: list = [session_id]

            if event_type:
                conditions.append("event_type = ?")
                params_plain.append(event_type)
            if participant:
                conditions.append("participants LIKE ?")
                params_plain.append(f"%{participant}%")
            if significance:
                conditions.append("significance = ?")
                params_plain.append(significance)

            where = " AND ".join(conditions)
            sql = f"SELECT * FROM events WHERE {where} ORDER BY timestamp DESC LIMIT ?"
            params_plain.append(last_n)

            rows = db.execute(sql, params_plain).fetchall()

        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def add_quest(
    session_id: str,
    title: str,
    description: str,
    given_by: str = "",
    status: str = "active",
) -> dict:
    """Add a new quest to the session tracker.

    Args:
        session_id: The session this quest belongs to
        title: Short quest title
        description: Full quest description and objectives
        given_by: NPC or entity who gave the quest
        status: Initial status — active, completed, failed, abandoned
    """
    db = get_game_db()
    try:
        db.execute(
            "INSERT INTO quests (session_id, title, description, given_by, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, title, description, given_by, status),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM quests WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        return {
            "quest_id": row["id"],
            "title": row["title"],
            "status": row["status"],
            "created_at": row["created_at"],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def update_quest(
    session_id: str,
    quest_title: str,
    status: str = "",
    notes: str = "",
) -> dict:
    """Update an existing quest's status or append notes.

    Args:
        session_id: The session the quest belongs to
        quest_title: Title of the quest to update (exact match)
        status: New status (active, completed, failed, abandoned) — empty to keep current
        notes: Text to append to existing quest notes
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM quests WHERE session_id = ? AND title = ?",
            (session_id, quest_title),
        ).fetchone()
        if not row:
            return {"error": f"Quest '{quest_title}' not found in session '{session_id}'"}

        quest = dict(row)
        if status:
            quest["status"] = status
        if notes:
            existing = quest.get("notes") or ""
            quest["notes"] = (existing + "\n" + notes).strip() if existing else notes

        db.execute(
            "UPDATE quests SET status = ?, notes = ?, updated_at = datetime('now') "
            "WHERE session_id = ? AND title = ?",
            (quest["status"], quest["notes"], session_id, quest_title),
        )
        db.commit()
        updated = db.execute(
            "SELECT * FROM quests WHERE session_id = ? AND title = ?",
            (session_id, quest_title),
        ).fetchone()
        return dict(updated)
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def list_quests(
    session_id: str,
    status: str = "",
) -> list[dict]:
    """List quests for a session, optionally filtered by status.

    Args:
        session_id: The session to list quests for
        status: Filter by status (active, completed, failed, abandoned) — empty for all
    """
    db = get_game_db()
    try:
        if status:
            rows = db.execute(
                "SELECT * FROM quests WHERE session_id = ? AND status = ? ORDER BY created_at",
                (session_id, status),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM quests WHERE session_id = ? ORDER BY created_at",
                (session_id,),
            ).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def add_foreshadow(
    session_id: str,
    thread: str,
    setup: str,
    intended_payoff: str = "",
) -> dict:
    """Plant a foreshadowing thread the DM intends to pay off later.

    Args:
        session_id: The session this thread belongs to
        thread: Short label for the thread (e.g. "recurring raven motif")
        setup: What the players experienced — the planted seed
        intended_payoff: DM's private notes on how this should resolve
    """
    db = get_game_db()
    try:
        db.execute(
            "INSERT INTO foreshadow (session_id, thread, setup, intended_payoff) VALUES (?, ?, ?, ?)",
            (session_id, thread, setup, intended_payoff),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM foreshadow WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        return dict(row)
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def get_foreshadow_threads(
    session_id: str,
    resolved: bool = False,
) -> list[dict]:
    """Get foreshadowing threads for a session.

    Args:
        session_id: The session to query
        resolved: If True, show resolved threads; if False (default), show unresolved
    """
    db = get_game_db()
    try:
        rows = db.execute(
            "SELECT * FROM foreshadow WHERE session_id = ? AND resolved = ? ORDER BY created_at",
            (session_id, 1 if resolved else 0),
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        db.close()


def resolve_foreshadow(
    session_id: str,
    thread: str,
    resolution: str,
) -> dict:
    """Mark a foreshadowing thread as resolved with payoff details.

    Args:
        session_id: The session this thread belongs to
        thread: The thread label to resolve (exact match)
        resolution: How the thread was paid off in-game
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM foreshadow WHERE session_id = ? AND thread = ?",
            (session_id, thread),
        ).fetchone()
        if not row:
            return {"error": f"Foreshadow thread '{thread}' not found in session '{session_id}'"}

        db.execute(
            "UPDATE foreshadow SET resolved = 1, resolution = ? WHERE session_id = ? AND thread = ?",
            (resolution, session_id, thread),
        )
        db.commit()
        updated = db.execute(
            "SELECT * FROM foreshadow WHERE session_id = ? AND thread = ?",
            (session_id, thread),
        ).fetchone()
        return dict(updated)
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
