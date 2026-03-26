#!/usr/bin/env python3
"""
Main orchestrator for Pathfinder data pipeline.

Usage:
    python3 src/run.py              # Run full pipeline
    python3 src/run.py --psrd-only  # Extract from PSRD only (no scraping)
    python3 src/run.py --scrape-only # Scrape aonprd only
    python3 src/run.py --merge-only # Merge existing data only
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


def run_psrd():
    print("=" * 60)
    print("PHASE 1: Download & Extract PSRD Data")
    print("=" * 60)
    from psrd_download import download_all
    download_all()
    from psrd_extract import main as extract_main
    extract_main()


def run_scrape():
    print("\n" + "=" * 60)
    print("PHASE 2: Scrape aonprd.com")
    print("=" * 60)
    from aonprd_scrape import main as scrape_main
    scrape_main()


def run_merge():
    print("\n" + "=" * 60)
    print("PHASE 3: Merge Data")
    print("=" * 60)
    from merge import main as merge_main
    merge_main()


def main():
    args = set(sys.argv[1:])

    if '--psrd-only' in args:
        run_psrd()
    elif '--scrape-only' in args:
        run_scrape()
    elif '--merge-only' in args:
        run_merge()
    else:
        run_psrd()
        run_scrape()
        run_merge()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == '__main__':
    main()
