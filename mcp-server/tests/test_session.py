"""Tests for session lifecycle tools."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import game_state
from tools.session import (
    create_session, get_session, list_sessions, join_session,
    save_session, load_session,
)


def test_create_session(game_db):
    result = create_session("Test Campaign", tone="gritty", setting="Golarion")
    assert "error" not in result
    assert result["name"] == "Test Campaign"
    assert result["tone"] == "gritty"
    assert "session_id" in result
    assert "created_at" in result


def test_get_session_not_found(game_db):
    result = get_session("nonexistent")
    assert "error" in result


def test_get_session_with_players(game_db):
    session = create_session("Player Test")
    sid = session["session_id"]

    join_session(sid, "p1", "Alice")
    join_session(sid, "p2", "Bob")

    result = get_session(sid)
    assert "error" not in result
    assert result["name"] == "Player Test"
    assert len(result["players"]) == 2
    names = {p["name"] for p in result["players"]}
    assert names == {"Alice", "Bob"}


def test_join_session(game_db):
    session = create_session("Join Test")
    sid = session["session_id"]

    result = join_session(sid, "player-abc", "Charlie")
    assert "error" not in result
    assert result["player_id"] == "player-abc"
    assert result["session_id"] == sid
    assert result["player_name"] == "Charlie"
    assert "joined_at" in result


def test_list_sessions(game_db):
    create_session("Session A")
    create_session("Session B", tone="comedic")

    result = list_sessions()
    assert len(result) >= 2
    names = {s["name"] for s in result}
    assert "Session A" in names
    assert "Session B" in names


def test_save_and_load_session(game_db):
    """Full roundtrip: create session, add players + data, save, modify, load, verify restore."""
    # Setup
    session = create_session("Save/Load Test")
    sid = session["session_id"]
    join_session(sid, "p-save", "SavePlayer")

    # Insert a character directly for the roundtrip test
    db = game_state.get_game_db()
    db.execute(
        "INSERT INTO characters (id, session_id, player_id, name, level, current_hp, max_hp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("char-1", sid, "p-save", "Test Hero", 5, 45, 50),
    )
    db.execute(
        "INSERT INTO events (session_id, event_type, summary) VALUES (?, ?, ?)",
        (sid, "combat", "Fought goblins"),
    )
    db.execute(
        "INSERT INTO quests (session_id, title, description) VALUES (?, ?, ?)",
        (sid, "Save the Village", "Protect it from goblins"),
    )
    db.commit()
    db.close()

    # Save
    snap = save_session(sid)
    assert "error" not in snap
    assert "snapshot_id" in snap

    # Modify the session (change character HP, add another event)
    db = game_state.get_game_db()
    db.execute("UPDATE characters SET current_hp = 10 WHERE id = 'char-1'")
    db.execute(
        "INSERT INTO events (session_id, event_type, summary) VALUES (?, ?, ?)",
        (sid, "travel", "Traveled to next town"),
    )
    db.commit()

    # Verify modification took effect
    row = db.execute("SELECT current_hp FROM characters WHERE id = 'char-1'").fetchone()
    assert row["current_hp"] == 10
    events = db.execute("SELECT * FROM events WHERE session_id = ?", (sid,)).fetchall()
    assert len(events) == 2
    db.close()

    # Load (restore from snapshot)
    result = load_session(sid)
    assert "error" not in result
    assert result["restored_from_snapshot_id"] == snap["snapshot_id"]

    # Verify restore
    db = game_state.get_game_db()
    row = db.execute("SELECT current_hp FROM characters WHERE id = 'char-1'").fetchone()
    assert row["current_hp"] == 45  # restored to original

    events = db.execute("SELECT * FROM events WHERE session_id = ?", (sid,)).fetchall()
    assert len(events) == 1  # only the original event
    assert events[0]["summary"] == "Fought goblins"
    db.close()


def test_load_session_no_snapshot(game_db):
    session = create_session("No Snapshot")
    result = load_session(session["session_id"])
    assert "error" in result
