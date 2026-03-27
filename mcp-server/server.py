#!/usr/bin/env python3
"""MCP server exposing Pathfinder 1e game data via SQLite queries."""

import json
import os
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DB_PATH = os.environ.get("PF_DB_PATH", str(Path(__file__).parent.parent / "db" / "pathfinder.db"))

mcp = FastMCP("pathfinder-data")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_list(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]


STUB_THRESHOLDS = {
    "spells": ("description", 100),
    "feats": ("benefit", 50),
    "archetypes": ("description", 50),
    "items": ("description", 50),
    "equipment": ("description", 50),
    "class_options": ("description", 50),
}


def is_stub(table: str, data: dict) -> bool:
    """Check if a record has incomplete data that should be enriched via web fetch."""
    field, min_len = STUB_THRESHOLDS.get(table, ("description", 50))
    text = data.get(field, "") or ""
    return len(text) < min_len and bool(data.get("url"))


def parse_data_field(results: list[dict], expand: bool = False, table: str = "") -> list[dict]:
    """If expand=True, parse the JSON 'data' field and merge it into the row.

    Adds _stub=True to records with incomplete descriptions that have a URL for enrichment.
    """
    if not expand:
        for r in results:
            r.pop("data", None)
        return results
    expanded = []
    for r in results:
        raw = r.pop("data", "{}")
        full = json.loads(raw)
        full.update({k: v for k, v in r.items() if k != "data"})
        if table:
            full["_stub"] = is_stub(table, full)
        expanded.append(full)
    return expanded


# ---------------------------------------------------------------------------
# Search tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_spells(
    query: str = "",
    school: str = "",
    class_name: str = "",
    max_level: int = -1,
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search spells by name, school, or class spell list.

    Args:
        query: Text to search in spell name (fuzzy FTS match)
        school: Filter by school (e.g. 'evocation', 'necromancy')
        class_name: Filter by class in spell_level (e.g. 'wizard', 'cleric')
        max_level: Only return spells up to this level for the given class (-1 = no filter)
        limit: Max results (default 20)
        expand: If True, return full spell data including description
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("s.rowid IN (SELECT rowid FROM fts_spells WHERE fts_spells MATCH ?)")
        params.append(f'name:{query}*')
    if school:
        conditions.append("s.school LIKE ?")
        params.append(f"%{school}%")
    if class_name:
        conditions.append("s.spell_level LIKE ?")
        params.append(f"%{class_name}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM spells s {where} ORDER BY s.name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()

    # Post-filter by max_level if class_name given
    if class_name and max_level >= 0:
        filtered = []
        for r in rows:
            sl = r.get("spell_level", "")
            # Check if "classname N" appears with N <= max_level
            import re
            pattern = rf'{re.escape(class_name)}\s+(\d+)'
            match = re.search(pattern, sl, re.IGNORECASE)
            if match and int(match.group(1)) <= max_level:
                filtered.append(r)
        rows = filtered

    return parse_data_field(rows, expand, table="spells")


@mcp.tool()
def search_feats(
    query: str = "",
    feat_type: str = "",
    prerequisite: str = "",
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search feats by name, type, or prerequisite.

    Args:
        query: Text to search in feat name
        feat_type: Filter by type (e.g. 'combat', 'metamagic', 'general', 'teamwork')
        prerequisite: Filter by text in prerequisites (e.g. 'Power Attack', 'BAB +6')
        limit: Max results (default 20)
        expand: If True, return full feat data including description and parsed prerequisites
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("f.rowid IN (SELECT rowid FROM fts_feats WHERE fts_feats MATCH ?)")
        params.append(f'name:{query}*')
    if feat_type:
        conditions.append("f.type LIKE ?")
        params.append(f"%{feat_type}%")
    if prerequisite:
        conditions.append("f.prerequisites LIKE ?")
        params.append(f"%{prerequisite}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM feats f {where} ORDER BY f.name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()
    return parse_data_field(rows, expand, table="feats")


@mcp.tool()
def search_classes(
    query: str = "",
    class_type: str = "",
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search classes by name or type.

    Args:
        query: Text to search in class name
        class_type: Filter by type ('base', 'core', 'hybrid', 'prestige', 'unchained')
        limit: Max results (default 20)
        expand: If True, return full class data including progression tables
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("name LIKE ?")
        params.append(f"%{query}%")
    if class_type:
        conditions.append("type = ?")
        params.append(class_type)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM classes {where} ORDER BY name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()
    return parse_data_field(rows, expand, table="classes")


@mcp.tool()
def search_archetypes(
    query: str = "",
    base_class: str = "",
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search archetypes by name or base class.

    Args:
        query: Text to search in archetype name
        base_class: Filter by base class (e.g. 'fighter', 'wizard', 'rogue')
        limit: Max results (default 20)
        expand: If True, return full archetype data including replaced features
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("a.rowid IN (SELECT rowid FROM fts_archetypes WHERE fts_archetypes MATCH ?)")
        params.append(f'name:{query}*')
    if base_class:
        conditions.append("a.base_class LIKE ?")
        params.append(f"%{base_class}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM archetypes a {where} ORDER BY a.name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()
    return parse_data_field(rows, expand, table="archetypes")


@mcp.tool()
def search_items(
    query: str = "",
    category: str = "",
    slot: str = "",
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search magic items by name, category, or slot.

    Args:
        query: Text to search in item name
        category: Filter by category (e.g. 'wondrous', 'weapon', 'armor', 'ring', 'rod', 'staff')
        slot: Filter by slot (e.g. 'head', 'shoulders', 'belt', 'hands')
        limit: Max results (default 20)
        expand: If True, return full item data including description and construction
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("i.rowid IN (SELECT rowid FROM fts_items WHERE fts_items MATCH ?)")
        params.append(f'name:{query}*')
    if category:
        conditions.append("i.category LIKE ?")
        params.append(f"%{category}%")
    if slot:
        conditions.append("i.slot LIKE ?")
        params.append(f"%{slot}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM items i {where} ORDER BY i.name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()
    return parse_data_field(rows, expand, table="items")


@mcp.tool()
def search_equipment(
    query: str = "",
    category: str = "",
    subcategory: str = "",
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search mundane equipment (weapons, armor, gear) by name or category.

    Args:
        query: Text to search in equipment name
        category: Filter by category ('weapon', 'armor', 'shield', 'gear')
        subcategory: Filter by subcategory (e.g. 'martial', 'simple', 'exotic', 'light', 'heavy')
        limit: Max results (default 20)
        expand: If True, return full equipment stats (damage, crit, AC, etc.)
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("e.rowid IN (SELECT rowid FROM fts_equipment WHERE fts_equipment MATCH ?)")
        params.append(f'name:{query}*')
    if category:
        conditions.append("e.category LIKE ?")
        params.append(f"%{category}%")
    if subcategory:
        conditions.append("e.subcategory LIKE ?")
        params.append(f"%{subcategory}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM equipment e {where} ORDER BY e.name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()
    return parse_data_field(rows, expand, table="equipment")


@mcp.tool()
def search_races(
    query: str = "",
    size: str = "",
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search races by name or size.

    Args:
        query: Text to search in race name
        size: Filter by size ('Small', 'Medium', 'Large')
        limit: Max results (default 20)
        expand: If True, return full race data including traits, alternate racial traits
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("name LIKE ?")
        params.append(f"%{query}%")
    if size:
        conditions.append("size = ?")
        params.append(size)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM races {where} ORDER BY name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()
    return parse_data_field(rows, expand, table="races")


@mcp.tool()
def search_class_options(
    query: str = "",
    option_type: str = "",
    base_class: str = "",
    limit: int = 20,
    expand: bool = False,
) -> list[dict]:
    """Search class options (domains, bloodlines, mysteries, patrons, subdomains).

    Args:
        query: Text to search in option name
        option_type: Filter by type ('domain', 'subdomain', 'bloodline', 'mystery', 'patron')
        base_class: Filter by class (e.g. 'cleric', 'sorcerer', 'oracle', 'witch')
        limit: Max results (default 20)
        expand: If True, return full data including spell lists and granted powers
    """
    db = get_db()
    conditions = []
    params = []

    if query:
        conditions.append("name LIKE ?")
        params.append(f"%{query}%")
    if option_type:
        conditions.append("type = ?")
        params.append(option_type)
    if base_class:
        conditions.append("base_class LIKE ?")
        params.append(f"%{base_class}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM class_options {where} ORDER BY name LIMIT ?"
    params.append(limit)

    rows = rows_to_list(db.execute(sql, params).fetchall())
    db.close()
    return parse_data_field(rows, expand, table="class_options")


@mcp.tool()
def get_skills() -> list[dict]:
    """Get all 26 Pathfinder skills with their key ability and trained-only status."""
    db = get_db()
    rows = rows_to_list(db.execute("SELECT * FROM skills ORDER BY name").fetchall())
    db.close()
    return parse_data_field(rows, expand=True, table="skills")


@mcp.tool()
def get_detail(table: str, id: str) -> dict | None:
    """Get full details for any game element by table and ID.

    Args:
        table: One of: skills, races, classes, archetypes, spells, feats, items, equipment, class_options
        id: The ID slug of the item
    """
    valid_tables = {"skills", "races", "classes", "archetypes", "spells", "feats", "items", "equipment", "class_options"}
    if table not in valid_tables:
        return {"error": f"Invalid table. Use one of: {', '.join(sorted(valid_tables))}"}

    db = get_db()
    row = db.execute(f"SELECT * FROM {table} WHERE id = ?", (id,)).fetchone()
    db.close()

    if not row:
        return {"error": f"Not found: {table}/{id}"}

    result = dict(row)
    raw = result.pop("data", "{}")
    full = json.loads(raw)
    full.update({k: v for k, v in result.items()})
    full["_stub"] = is_stub(table, full)
    return full


@mcp.tool()
def check_feat_prerequisites(
    feat_name: str,
    character_bab: int = 0,
    character_level: int = 0,
    character_feats: list[str] = [],
    character_abilities: dict = {},
    character_skills: dict = {},
) -> dict:
    """Check if a character meets the prerequisites for a feat.

    Args:
        feat_name: Name of the feat to check
        character_bab: Character's base attack bonus
        character_level: Character's total level
        character_feats: List of feat names the character has
        character_abilities: Dict of ability scores (e.g. {"str": 13, "dex": 15})
        character_skills: Dict of skill ranks (e.g. {"Acrobatics": 5, "Perception": 10})

    Returns:
        Dict with 'qualified' bool, 'met' list, and 'unmet' list of prerequisites
    """
    db = get_db()
    row = db.execute("SELECT data FROM feats WHERE name LIKE ? LIMIT 1", (feat_name,)).fetchone()
    db.close()

    if not row:
        return {"error": f"Feat not found: {feat_name}"}

    feat_data = json.loads(row["data"])
    parsed = feat_data.get("parsed_prerequisites", [])

    if not parsed:
        return {
            "feat": feat_name,
            "qualified": True,
            "note": "No parsed prerequisites available — check raw text",
            "raw_prerequisites": feat_data.get("prerequisites", ""),
        }

    met = []
    unmet = []

    feat_names_lower = [f.lower() for f in character_feats]
    abilities_lower = {k.lower(): v for k, v in character_abilities.items()}

    for prereq in parsed:
        ptype = prereq.get("type", "")
        pname = prereq.get("name", "")
        pvalue = prereq.get("value", 0)

        if ptype == "ability":
            score = abilities_lower.get(pname.lower()[:3], 0)
            if score >= pvalue:
                met.append(f"{pname} {pvalue} (have {score})")
            else:
                unmet.append(f"{pname} {pvalue} (have {score})")
        elif ptype == "bab":
            if character_bab >= pvalue:
                met.append(f"BAB +{pvalue} (have +{character_bab})")
            else:
                unmet.append(f"BAB +{pvalue} (have +{character_bab})")
        elif ptype == "feat":
            if pname.lower() in feat_names_lower:
                met.append(f"Feat: {pname}")
            else:
                unmet.append(f"Feat: {pname}")
        elif ptype == "skill":
            ranks = character_skills.get(pname, 0)
            if ranks >= pvalue:
                met.append(f"{pname} {pvalue} ranks (have {ranks})")
            else:
                unmet.append(f"{pname} {pvalue} ranks (have {ranks})")
        else:
            met.append(f"(unchecked) {ptype}: {pname} {pvalue}")

    return {
        "feat": feat_name,
        "qualified": len(unmet) == 0,
        "met": met,
        "unmet": unmet,
    }


@mcp.tool()
def check_archetype_compatibility(
    base_class: str,
    archetype_names: list[str],
) -> dict:
    """Check if multiple archetypes for the same class are compatible (don't replace the same features).

    Args:
        base_class: The base class name (e.g. 'fighter', 'rogue')
        archetype_names: List of archetype names to check compatibility for
    """
    db = get_db()
    placeholders = ",".join("?" * len(archetype_names))
    rows = db.execute(
        f"SELECT name, data FROM archetypes WHERE base_class LIKE ? AND name IN ({placeholders})",
        [f"%{base_class}%"] + archetype_names
    ).fetchall()
    db.close()

    if not rows:
        return {"error": f"No archetypes found for {base_class} with names: {archetype_names}"}

    archetypes = {}
    all_replaced = {}

    for row in rows:
        data = json.loads(row["data"])
        name = row["name"]
        replaced = data.get("replaced_features", [])
        archetypes[name] = replaced
        for feature in replaced:
            fl = feature.lower().strip()
            if fl not in all_replaced:
                all_replaced[fl] = []
            all_replaced[fl].append(name)

    conflicts = {
        feature: arches
        for feature, arches in all_replaced.items()
        if len(arches) > 1
    }

    return {
        "base_class": base_class,
        "archetypes": {name: feats for name, feats in archetypes.items()},
        "compatible": len(conflicts) == 0,
        "conflicts": conflicts if conflicts else None,
        "not_found": [n for n in archetype_names if n not in archetypes],
    }


@mcp.tool()
def cache_entry(
    table: str,
    id: str,
    name: str,
    data: dict,
    source: str = "web",
    **columns,
) -> dict:
    """Cache a new game data entry found via web search into the local database.

    Use this when a search returns no results and the agent finds the data online.
    The entry will be available for all future queries.

    Args:
        table: Target table (skills, races, classes, archetypes, spells, feats, items, equipment, class_options)
        id: ID slug for the entry (e.g. 'web-improved-familiar')
        name: Display name (e.g. 'Improved Familiar')
        data: Full data dict to store as JSON
        source: Source identifier (default 'web')
        **columns: Additional indexed columns specific to the table
                   (e.g. school='conjuration', spell_level='wizard 3' for spells)
    """
    valid_tables = {"skills", "races", "classes", "archetypes", "spells", "feats", "items", "equipment", "class_options"}
    if table not in valid_tables:
        return {"error": f"Invalid table. Use one of: {', '.join(sorted(valid_tables))}"}

    # Column definitions per table (excluding id, name, data which are universal)
    table_columns = {
        "skills":        ["ability", "trained_only"],
        "races":         ["source", "size", "speed"],
        "classes":       ["source", "type", "hit_die", "alignment"],
        "archetypes":    ["source", "base_class", "url"],
        "spells":        ["source", "school", "subschool", "descriptor", "spell_level", "url"],
        "feats":         ["source", "type", "prerequisites", "url"],
        "items":         ["source", "category", "slot", "aura", "cl", "price"],
        "equipment":     ["source", "category", "subcategory", "price", "weight"],
        "class_options": ["source", "type", "base_class"],
    }

    extra_cols = table_columns.get(table, [])
    col_names = ["id", "name"] + extra_cols + ["data"]
    placeholders = ",".join("?" * len(col_names))

    # Build values: id, name, then extra columns from data/columns, then JSON blob
    data_with_meta = {**data, "name": name, "source": source}
    values = [id, name]
    for col in extra_cols:
        val = columns.get(col, data.get(col, data_with_meta.get(col)))
        if isinstance(val, (list, dict)):
            val = json.dumps(val)
        values.append(val)
    values.append(json.dumps(data_with_meta))

    db = get_db()
    try:
        db.execute(
            f"INSERT OR REPLACE INTO {table} ({','.join(col_names)}) VALUES ({placeholders})",
            values
        )
        # Rebuild FTS for tables that have it
        fts_tables = {"spells", "feats", "items", "archetypes", "equipment"}
        if table in fts_tables:
            db.execute(f"INSERT INTO fts_{table}(fts_{table}) VALUES('rebuild')")
        db.commit()
        db.close()
        return {"status": "cached", "table": table, "id": id, "name": name}
    except Exception as e:
        db.close()
        return {"error": str(e)}


@mcp.tool()
def db_stats() -> dict:
    """Get row counts for all tables in the database."""
    db = get_db()
    tables = ["skills", "races", "classes", "archetypes", "spells", "feats", "items", "equipment", "class_options"]
    stats = {}
    for t in tables:
        count = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        stats[t] = count
    db.close()
    return stats


# ---------------------------------------------------------------------------
# Guide search
# ---------------------------------------------------------------------------

GUIDES_DIR = str(Path(__file__).parent.parent / "data" / "guides")


@mcp.tool()
def search_guides(
    query: str,
    class_name: str = "",
    limit: int = 10,
) -> list[dict]:
    """Search optimization guides for build advice, feat/spell ratings, and recommendations.

    Searches across all 79 community guides (grep on markdown files).
    Returns matching passages with surrounding context.

    Args:
        query: Text to search for (e.g. 'sidestep secret', 'power attack', 'battle mystery')
        class_name: Optional - limit search to guides for this class (e.g. 'oracle', 'fighter')
        limit: Max number of matching passages to return (default 10)

    Returns:
        List of dicts with guide, file, and matching passage with context
    """
    import subprocess

    # Build grep command
    search_path = GUIDES_DIR
    if class_name:
        # Find guide dirs that match the class
        matching_dirs = []
        for idx_path in Path(GUIDES_DIR).glob("*/index.md"):
            with open(idx_path) as f:
                content = f.read(500)
            if class_name.lower() in content.lower():
                matching_dirs.append(str(idx_path.parent))
        for guide_path in Path(GUIDES_DIR).glob("*/guide.md"):
            with open(guide_path) as f:
                content = f.read(500)
            if class_name.lower() in content.lower():
                matching_dirs.append(str(guide_path.parent))
        if not matching_dirs:
            return [{"note": f"No guides found for class '{class_name}'"}]
        search_paths = matching_dirs
    else:
        search_paths = [GUIDES_DIR]

    results = []
    for sp in (search_paths if class_name else [GUIDES_DIR]):
        try:
            proc = subprocess.run(
                ["grep", "-ril", "--include=*.md", query, sp],
                capture_output=True, text=True, timeout=10
            )
            matching_files = [f for f in proc.stdout.strip().split("\n") if f]

            for fpath in matching_files[:limit * 2]:
                # Get matching lines with context
                proc2 = subprocess.run(
                    ["grep", "-in", "-C", "2", "-m", "3", query, fpath],
                    capture_output=True, text=True, timeout=5
                )
                if proc2.stdout.strip():
                    # Extract guide name from path
                    rel = os.path.relpath(fpath, GUIDES_DIR)
                    guide_dir = rel.split(os.sep)[0]

                    results.append({
                        "guide": guide_dir,
                        "file": rel,
                        "matches": proc2.stdout.strip()[:1500],
                    })
                    if len(results) >= limit:
                        break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        if len(results) >= limit:
            break

    if not results:
        return [{"note": f"No matches found for '{query}'" + (f" in {class_name} guides" if class_name else "")}]

    return results


@mcp.tool()
def get_guide_index() -> str:
    """Get the complete guide index listing all available optimization guides.

    Returns the INDEX.md content which lists all guides organized by class
    with entry points and coverage summary. Use this to find the right guide
    before reading specific sections.
    """
    index_path = os.path.join(GUIDES_DIR, "INDEX.md")
    if not os.path.exists(index_path):
        return "INDEX.md not found"
    with open(index_path) as f:
        return f.read()


@mcp.tool()
def get_reference(topic: str) -> str:
    """Get plugin reference documentation by topic.

    Available topics:
        - 'format' — Character sheet format specification (FORMAT.md)
        - 'advisor' — Advisor behavior rules (combat, dice, state management)
        - 'mcp' — MCP tool reference and stub enrichment protocol
        - 'characters' — Character sheet conventions
        - 'campaign' — Campaign data conventions
        - 'guides' — Guide usage instructions

    Args:
        topic: One of: format, advisor, mcp, characters, campaign, guides
    """
    topic_files = {
        "format": "data/characters/FORMAT.md",
        "advisor": "docs/advisor.md",
        "mcp": "docs/mcp-tools.md",
        "characters": "docs/characters.md",
        "campaign": "docs/campaign.md",
        "guides": "docs/guides.md",
    }

    if topic not in topic_files:
        return f"Unknown topic '{topic}'. Available: {', '.join(sorted(topic_files.keys()))}"

    plugin_root = Path(__file__).parent.parent
    fpath = plugin_root / topic_files[topic]
    if not fpath.exists():
        return f"File not found: {topic_files[topic]}"
    with open(fpath) as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()
