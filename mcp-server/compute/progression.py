"""Class data lookup from the pathfinder.db rules database."""

import json
import sqlite3
from pathlib import Path


def _default_rules_db_path() -> str:
    """Return the default path to pathfinder.db."""
    try:
        from server import DB_PATH
        return DB_PATH
    except ImportError:
        return str(Path(__file__).parent.parent.parent / "db" / "pathfinder.db")


def lookup_class_data(class_name: str, rules_db_path: str = None) -> dict:
    """Look up a class's full data from pathfinder.db.

    Searches the classes table using a LIKE query on name, parses the JSON
    data column, and returns the full class record with parsed data merged in.

    Args:
        class_name: Class name to search for (e.g. "Fighter", "Wizard")
        rules_db_path: Path to pathfinder.db. Defaults to server.DB_PATH.

    Returns:
        dict with class info including parsed 'data' fields (progression,
        spellcasting, hit_die, skill_ranks_per_level, class_skills, etc.)
        or {"error": "..."} if not found.
    """
    if rules_db_path is None:
        rules_db_path = _default_rules_db_path()

    conn = sqlite3.connect(rules_db_path)
    conn.row_factory = sqlite3.Row
    try:
        # Try exact match first, then LIKE
        row = conn.execute(
            "SELECT * FROM classes WHERE LOWER(name) = LOWER(?) LIMIT 1",
            (class_name,),
        ).fetchone()
        if not row:
            row = conn.execute(
                "SELECT * FROM classes WHERE name LIKE ? LIMIT 1",
                (f"%{class_name}%",),
            ).fetchone()
        if not row:
            return {"error": f"Class '{class_name}' not found in rules database"}

        result = dict(row)
        if "data" in result and result["data"]:
            data = json.loads(result["data"])
            result.update(data)
            del result["data"]
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()
