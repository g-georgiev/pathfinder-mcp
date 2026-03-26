"""
Inspect PSRD-Data SQLite database schemas and sample data.
Run this after downloading to understand the structure before writing extraction queries.
"""

import os
import sys
import sqlite3
import json

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'psrd')


def inspect_db(db_path: str, sample_limit: int = 3):
    """Print schema and sample data for a SQLite database."""
    db_name = os.path.basename(db_path)
    print(f"\n{'=' * 70}")
    print(f"DATABASE: {db_name}")
    print(f"{'=' * 70}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\nTables ({len(tables)}): {', '.join(tables)}")

    for table in tables:
        print(f"\n--- {table} ---")

        # Schema
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        col_info = [(c['name'], c['type'], 'PK' if c['pk'] else '') for c in columns]
        print(f"  Columns: {', '.join(f'{n} ({t}){' PK' if pk else ''}' for n, t, pk in col_info)}")

        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")

        # Sample data
        if count > 0 and sample_limit > 0:
            cursor.execute(f"SELECT * FROM {table} LIMIT {sample_limit}")
            rows = cursor.fetchall()
            for i, row in enumerate(rows):
                row_dict = dict(row)
                # Truncate long values for readability
                for k, v in row_dict.items():
                    if isinstance(v, str) and len(v) > 200:
                        row_dict[k] = v[:200] + '...'
                print(f"  Sample {i+1}: {json.dumps(row_dict, indent=4, ensure_ascii=False)}")

    conn.close()


def inspect_all(sample_limit: int = 3):
    """Inspect all downloaded PSRD databases."""
    if not os.path.isdir(RAW_DIR):
        print(f"No PSRD data directory found at {RAW_DIR}")
        print("Run psrd_download.py first.")
        return

    db_files = sorted(f for f in os.listdir(RAW_DIR) if f.endswith('.db'))
    if not db_files:
        print(f"No .db files found in {RAW_DIR}")
        return

    print(f"Found {len(db_files)} database files: {', '.join(db_files)}")

    for db_file in db_files:
        inspect_db(os.path.join(RAW_DIR, db_file), sample_limit=sample_limit)


if __name__ == '__main__':
    sample = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    inspect_all(sample_limit=sample)
