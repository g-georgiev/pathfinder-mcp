"""Tests for campaign memory tools — events, quests, foreshadowing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import game_state
from tools.session import create_session
from tools.campaign import (
    log_event, recall_events, add_quest, update_quest, list_quests,
    add_foreshadow, get_foreshadow_threads, resolve_foreshadow,
)


def _make_session(name="CampaignTest"):
    """Helper to create a session and return its ID."""
    return create_session(name)["session_id"]


# ---------- Events ----------

def test_log_event(game_db):
    sid = _make_session()
    result = log_event(sid, "combat", "Party fought dire wolves", participants=["Valeros", "Merisiel"])
    assert "error" not in result
    assert result["event_type"] == "combat"
    assert "event_id" in result
    assert "timestamp" in result


def test_recall_events_no_query(game_db):
    sid = _make_session()
    log_event(sid, "combat", "Fought goblins at the bridge", significance="major")
    log_event(sid, "roleplay", "Negotiated with merchant")
    log_event(sid, "travel", "Crossed the desert")

    # Recall all
    results = recall_events(sid)
    assert len(results) == 3

    # Filter by type
    results = recall_events(sid, event_type="combat")
    assert len(results) == 1
    assert results[0]["event_type"] == "combat"

    # Filter by significance
    results = recall_events(sid, significance="major")
    assert len(results) == 1


def test_recall_events_by_participant(game_db):
    sid = _make_session()
    log_event(sid, "combat", "Valeros slew the ogre", participants=["Valeros"])
    log_event(sid, "roleplay", "Merisiel picked the lock", participants=["Merisiel"])

    results = recall_events(sid, participant="Valeros")
    assert len(results) == 1
    assert "Valeros" in results[0]["summary"]


def test_recall_events_fts(game_db):
    sid = _make_session()
    log_event(sid, "combat", "Fought goblins at the bridge")
    log_event(sid, "roleplay", "Negotiated with the goblin chief")
    log_event(sid, "travel", "Crossed the desert to reach mountains")

    # FTS search for "goblin"
    results = recall_events(sid, query="goblin*")
    assert len(results) >= 1
    for r in results:
        assert "goblin" in r["summary"].lower()


def test_recall_events_last_n(game_db):
    sid = _make_session()
    for i in range(10):
        log_event(sid, "travel", f"Event number {i}")

    results = recall_events(sid, last_n=3)
    assert len(results) == 3


# ---------- Quests ----------

def test_add_quest(game_db):
    sid = _make_session()
    result = add_quest(sid, "Find the Amulet", "Locate the lost amulet of Iomedae", given_by="High Priestess")
    assert "error" not in result
    assert result["title"] == "Find the Amulet"
    assert result["status"] == "active"
    assert "quest_id" in result


def test_update_quest_status(game_db):
    sid = _make_session()
    add_quest(sid, "Rescue the Prince", "Free the prince from the dungeon")

    result = update_quest(sid, "Rescue the Prince", status="completed")
    assert "error" not in result
    assert result["status"] == "completed"


def test_update_quest_notes(game_db):
    sid = _make_session()
    add_quest(sid, "Dragon Hunt", "Slay the dragon")

    update_quest(sid, "Dragon Hunt", notes="Found dragon tracks near cave")
    result = update_quest(sid, "Dragon Hunt", notes="Dragon is a red wyrm")
    assert "Dragon is a red wyrm" in result["notes"]
    assert "Found dragon tracks" in result["notes"]


def test_update_quest_not_found(game_db):
    sid = _make_session()
    result = update_quest(sid, "Nonexistent Quest", status="completed")
    assert "error" in result


def test_list_quests(game_db):
    sid = _make_session()
    add_quest(sid, "Quest A", "Description A")
    add_quest(sid, "Quest B", "Description B", status="completed")
    add_quest(sid, "Quest C", "Description C")

    # All quests
    all_quests = list_quests(sid)
    assert len(all_quests) == 3

    # Active only
    active = list_quests(sid, status="active")
    assert len(active) == 2

    # Completed only
    completed = list_quests(sid, status="completed")
    assert len(completed) == 1
    assert completed[0]["title"] == "Quest B"


# ---------- Foreshadowing ----------

def test_add_foreshadow(game_db):
    sid = _make_session()
    result = add_foreshadow(
        sid,
        thread="Recurring raven motif",
        setup="A raven appeared watching the party at three key moments",
        intended_payoff="The raven is a polymorphed spy for the BBEG",
    )
    assert "error" not in result
    assert result["thread"] == "Recurring raven motif"
    assert result["resolved"] == 0


def test_get_foreshadow_threads_unresolved(game_db):
    sid = _make_session()
    add_foreshadow(sid, "Thread A", "Setup A")
    add_foreshadow(sid, "Thread B", "Setup B")

    threads = get_foreshadow_threads(sid, resolved=False)
    assert len(threads) == 2


def test_resolve_foreshadow(game_db):
    sid = _make_session()
    add_foreshadow(sid, "Mysterious symbol", "Symbol carved on dungeon walls")

    result = resolve_foreshadow(sid, "Mysterious symbol", "Symbol was a ward against the lich")
    assert "error" not in result
    assert result["resolved"] == 1
    assert result["resolution"] == "Symbol was a ward against the lich"

    # Now unresolved should be empty
    unresolved = get_foreshadow_threads(sid, resolved=False)
    assert len(unresolved) == 0

    # Resolved should have 1
    resolved = get_foreshadow_threads(sid, resolved=True)
    assert len(resolved) == 1


def test_resolve_foreshadow_not_found(game_db):
    sid = _make_session()
    result = resolve_foreshadow(sid, "nonexistent", "whatever")
    assert "error" in result
