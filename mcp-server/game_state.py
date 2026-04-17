"""Game state database management for the AI DM project.

Provides get_game_db() for accessing game_state.db (sessions, characters,
combat, campaign memory). Auto-creates the database on first access.
"""

import os
import sqlite3
from pathlib import Path

GAME_STATE_DB_PATH = os.environ.get(
    "GS_DB_PATH",
    str(Path(__file__).parent.parent / "db" / "game_state.db"),
)

SCHEMA_DDL = """
-- Session lifecycle
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tone TEXT DEFAULT 'heroic',
    setting TEXT DEFAULT '',
    dm_notes TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Players in a session
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    name TEXT NOT NULL,
    joined_at TEXT DEFAULT (datetime('now'))
);

-- Character sheets (JSON blob + indexed fields)
CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    player_id TEXT REFERENCES players(id),
    name TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    classes TEXT DEFAULT '',
    race TEXT DEFAULT '',
    is_npc INTEGER DEFAULT 0,
    status TEXT DEFAULT 'alive',
    current_hp INTEGER DEFAULT 0,
    max_hp INTEGER DEFAULT 0,
    data TEXT NOT NULL DEFAULT '{}',
    computed TEXT NOT NULL DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_characters_session ON characters(session_id);
CREATE INDEX IF NOT EXISTS idx_characters_player ON characters(player_id);

-- Active conditions on characters
CREATE TABLE IF NOT EXISTS conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    character_id TEXT NOT NULL REFERENCES characters(id),
    condition_name TEXT NOT NULL,
    duration_rounds INTEGER DEFAULT -1,
    source TEXT DEFAULT '',
    applied_at TEXT DEFAULT (datetime('now'))
);

-- Combat encounters
CREATE TABLE IF NOT EXISTS combats (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    status TEXT DEFAULT 'active',
    round INTEGER DEFAULT 1,
    current_turn_index INTEGER DEFAULT 0,
    turn_order TEXT NOT NULL DEFAULT '[]',
    started_at TEXT DEFAULT (datetime('now'))
);

-- Campaign event log
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    participants TEXT DEFAULT '[]',
    location TEXT DEFAULT '',
    significance TEXT DEFAULT 'minor',
    timestamp TEXT DEFAULT (datetime('now'))
);

-- Quest tracking
CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    given_by TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Foreshadowing threads
CREATE TABLE IF NOT EXISTS foreshadow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    thread TEXT NOT NULL,
    setup TEXT NOT NULL,
    intended_payoff TEXT DEFAULT '',
    resolution TEXT DEFAULT '',
    resolved INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Session snapshots for save/load
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    snapshot_data TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

# FTS5 must be created separately (CREATE VIRTUAL TABLE doesn't support IF NOT EXISTS cleanly)
FTS_DDL = """
CREATE VIRTUAL TABLE IF NOT EXISTS fts_events USING fts5(
    summary,
    content='events',
    content_rowid='id'
);
"""

_initialized = False


def _init_db(conn: sqlite3.Connection) -> None:
    """Create tables and indexes if they don't exist."""
    conn.executescript(SCHEMA_DDL)
    conn.executescript(FTS_DDL)
    conn.commit()


def get_game_db() -> sqlite3.Connection:
    """Get a connection to game_state.db, auto-creating on first access."""
    global _initialized
    conn = sqlite3.connect(GAME_STATE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if not _initialized:
        _init_db(conn)
        _initialized = True
    return conn
