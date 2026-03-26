#!/usr/bin/env python3
"""Build SQLite database with FTS5 from the JSON data pipeline output."""

import json
import sqlite3
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "scripts" / "data" / "output"
DB_PATH = Path(__file__).parent / "pathfinder.db"


def load_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  SKIP {filename} (not found)")
        return None
    with open(path) as f:
        return json.load(f)


def create_tables(cur: sqlite3.Cursor):
    cur.executescript("""
        -- Skills
        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            ability TEXT,
            trained_only INTEGER DEFAULT 0,
            data TEXT NOT NULL
        );

        -- Races
        CREATE TABLE IF NOT EXISTS races (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            size TEXT,
            speed INTEGER,
            data TEXT NOT NULL
        );

        -- Classes
        CREATE TABLE IF NOT EXISTS classes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            type TEXT,  -- 'base', 'core', 'hybrid', 'prestige', 'unchained'
            hit_die TEXT,
            alignment TEXT,
            data TEXT NOT NULL
        );

        -- Archetypes
        CREATE TABLE IF NOT EXISTS archetypes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            base_class TEXT,
            url TEXT,
            data TEXT NOT NULL
        );

        -- Spells
        CREATE TABLE IF NOT EXISTS spells (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            school TEXT,
            subschool TEXT,
            descriptor TEXT,
            spell_level TEXT,
            url TEXT,
            data TEXT NOT NULL
        );

        -- Feats
        CREATE TABLE IF NOT EXISTS feats (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            type TEXT,
            prerequisites TEXT,
            url TEXT,
            data TEXT NOT NULL
        );

        -- Magic Items
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            category TEXT,
            slot TEXT,
            aura TEXT,
            cl INTEGER,
            price TEXT,
            data TEXT NOT NULL
        );

        -- Equipment (mundane)
        CREATE TABLE IF NOT EXISTS equipment (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            category TEXT,  -- 'weapon', 'armor', 'shield', 'gear'
            subcategory TEXT,
            price TEXT,
            weight TEXT,
            data TEXT NOT NULL
        );

        -- Class Options (domains, bloodlines, mysteries, patrons, subdomains)
        CREATE TABLE IF NOT EXISTS class_options (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source TEXT,
            type TEXT,  -- 'domain', 'subdomain', 'bloodline', 'mystery', 'patron'
            base_class TEXT,
            data TEXT NOT NULL
        );

        -- FTS5 virtual tables for full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_spells USING fts5(
            id, name, school, descriptor, spell_level,
            content='spells', content_rowid='rowid'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_feats USING fts5(
            id, name, type, prerequisites,
            content='feats', content_rowid='rowid'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_items USING fts5(
            id, name, category, slot, aura,
            content='items', content_rowid='rowid'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_archetypes USING fts5(
            id, name, base_class,
            content='archetypes', content_rowid='rowid'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_equipment USING fts5(
            id, name, category, subcategory,
            content='equipment', content_rowid='rowid'
        );
    """)


def slugify(*parts: str) -> str:
    return "-".join(
        p.lower().replace(" ", "-").replace("'", "").replace(",", "")
        for p in parts if p
    )


def seed_skills(cur, data):
    for item in data:
        cur.execute(
            "INSERT OR IGNORE INTO skills (id, name, ability, trained_only, data) VALUES (?, ?, ?, ?, ?)",
            (slugify(item["name"]), item["name"], item.get("ability"),
             1 if item.get("trained_only") else 0, json.dumps(item))
        )


def seed_races(cur, data):
    for item in data:
        speed = item.get("speed")
        if isinstance(speed, list):
            land = next((s["value"] for s in speed if s.get("type") == "land"), None)
            speed = land
        cur.execute(
            "INSERT OR IGNORE INTO races (id, name, source, size, speed, data) VALUES (?, ?, ?, ?, ?, ?)",
            (slugify(item.get("source", ""), item["name"]), item["name"],
             item.get("source"), item.get("size"), speed,
             json.dumps(item))
        )


def seed_classes(cur, data):
    for item in data:
        cls_type = item.get("type", "base")
        cur.execute(
            "INSERT OR IGNORE INTO classes (id, name, source, type, hit_die, alignment, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (slugify(item.get("source", ""), item["name"]), item["name"],
             item.get("source"), cls_type, item.get("hit_die"),
             item.get("alignment"), json.dumps(item))
        )


def seed_archetypes(cur, data):
    for item in data:
        base = item.get("base_class", "")
        cur.execute(
            "INSERT OR IGNORE INTO archetypes (id, name, source, base_class, url, data) VALUES (?, ?, ?, ?, ?, ?)",
            (slugify(item.get("source", ""), base, item["name"]), item["name"],
             item.get("source"), base, item.get("url"),
             json.dumps(item))
        )


def seed_spells(cur, data):
    for item in data:
        spell_level = item.get("spell_level", "")
        if isinstance(spell_level, dict):
            spell_level = ", ".join(f"{k} {v}" for k, v in spell_level.items())
        cur.execute(
            "INSERT OR IGNORE INTO spells (id, name, source, school, subschool, descriptor, spell_level, url, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (slugify(item.get("source", ""), item["name"]), item["name"],
             item.get("source"), item.get("school"), item.get("subschool"),
             item.get("descriptor"), spell_level, item.get("url"),
             json.dumps(item))
        )


def seed_feats(cur, data):
    for item in data:
        prereqs = item.get("prerequisites", "")
        if isinstance(prereqs, list):
            prereqs = ", ".join(str(p) for p in prereqs)
        feat_type = item.get("type", item.get("feat_type", ""))
        if isinstance(feat_type, list):
            feat_type = ", ".join(feat_type)
        cur.execute(
            "INSERT OR IGNORE INTO feats (id, name, source, type, prerequisites, url, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (slugify(item.get("source", ""), item["name"]), item["name"],
             item.get("source"), feat_type, prereqs, item.get("url"),
             json.dumps(item))
        )


def seed_items(cur, data):
    for item in data:
        cur.execute(
            "INSERT OR IGNORE INTO items (id, name, source, category, slot, aura, cl, price, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (slugify(item.get("source", ""), item.get("category", ""), item["name"]),
             item["name"], item.get("source"), item.get("category"),
             item.get("slot"), item.get("aura"), item.get("cl"),
             item.get("price"), json.dumps(item))
        )


def seed_equipment(cur, data):
    for item in data:
        cur.execute(
            "INSERT OR IGNORE INTO equipment (id, name, source, category, subcategory, price, weight, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (slugify(item.get("source", ""), item.get("category", ""), item["name"]),
             item["name"], item.get("source"), item.get("category"),
             item.get("subcategory"), item.get("price"), item.get("weight"),
             json.dumps(item))
        )


def seed_class_options(cur, data):
    # class_options.json is a dict keyed by category
    type_map = {
        "domains": ("domain", "cleric"),
        "subdomains": ("subdomain", "cleric"),
        "bloodlines": ("bloodline", "sorcerer"),
        "oracle_mysteries": ("mystery", "oracle"),
        "witch_patrons": ("patron", "witch"),
    }
    for key, items in data.items():
        opt_type, base_class = type_map.get(key, (key, ""))
        for item in items:
            cur.execute(
                "INSERT OR IGNORE INTO class_options (id, name, source, type, base_class, data) VALUES (?, ?, ?, ?, ?, ?)",
                (slugify(item.get("source", ""), opt_type, item["name"]),
                 item["name"], item.get("source"), opt_type, base_class,
                 json.dumps(item))
            )


def rebuild_fts(cur):
    """Populate FTS5 indexes from content tables."""
    for table in ["spells", "feats", "items", "archetypes", "equipment"]:
        cur.execute(f"INSERT INTO fts_{table}(fts_{table}) VALUES('rebuild')")


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")

    print("Creating tables...")
    create_tables(cur)

    # Seed each table — prefer merged files where available
    seeds = [
        ("skills",        "skills.json",             seed_skills),
        ("races",         "races.json",              seed_races),
        ("classes",       "classes.json",            seed_classes),
        ("archetypes",    "merged_archetypes.json",  seed_archetypes),
        ("spells",        "merged_spells.json",      seed_spells),
        ("feats",         "merged_feats.json",       seed_feats),
        ("items",         "items.json",              seed_items),
        ("equipment",     "equipment.json",          seed_equipment),
        ("class_options", "class_options.json",       seed_class_options),
    ]

    for table_name, filename, seed_fn in seeds:
        data = load_json(filename)
        if data:
            seed_fn(cur, data)
            count = cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"  {table_name}: {count} rows")

    print("Building FTS indexes...")
    rebuild_fts(cur)

    conn.commit()

    # Report final size
    size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"\nDatabase built: {DB_PATH} ({size_mb:.1f} MB)")
    conn.close()


if __name__ == "__main__":
    main()
