"""
Download PSRD-Data SQLite databases from GitHub.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import download_file

PSRD_BASE_URL = "https://github.com/devonjones/PSRD-Data/raw/refs/heads/release"
RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'psrd')

# Available databases in PSRD-Data
DATABASES = {
    'core_rulebook': 'book-cr.db',
    'advanced_players_guide': 'book-apg.db',
    'ultimate_magic': 'book-um.db',
    'ultimate_combat': 'book-uc.db',
    'advanced_race_guide': 'book-arg.db',
    'ultimate_equipment': 'book-ue.db',
    'mythic_adventures': 'book-ma.db',
    'technology_guide': 'book-tech.db',
    'index': 'index.db',
}


def download_all(force: bool = False):
    os.makedirs(RAW_DIR, exist_ok=True)

    for label, filename in DATABASES.items():
        dest = os.path.join(RAW_DIR, filename)
        if os.path.exists(dest) and not force:
            print(f"  Skipping {label} ({filename}) - already exists")
            continue
        url = f"{PSRD_BASE_URL}/{filename}"
        try:
            download_file(url, dest)
        except Exception as e:
            print(f"  ERROR downloading {label}: {e}")


if __name__ == '__main__':
    force = '--force' in sys.argv
    print("Downloading PSRD-Data SQLite databases...")
    download_all(force=force)
    print("Done.")
