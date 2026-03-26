"""
Merge PSRD and aonprd data into final normalized output.

Strategy:
  - PSRD provides the rich, structured data (class progressions, spell details,
    item stats, etc.) for core books
  - aonprd provides the comprehensive INDEX (spell names, feat names, archetype
    replacement info) covering ALL Paizo books
  - For spells: merge PSRD details with aonprd index, keeping PSRD details where
    available and adding aonprd-only spells as index entries
  - For feats: same approach
  - For archetypes: use aonprd's explicit "Replaces" column to improve PSRD's
    regex-parsed replacement data, and add all aonprd-only archetypes
"""

import os
import sys
import re
import json
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(__file__))
from models import (
    Spell, SpellClassLevel, Feat, Archetype, ArchetypeModification,
    ArchetypeFeature, save_json
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')


def load_json(filename: str) -> list:
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        print(f"  WARNING: {path} not found")
        return []
    with open(path) as f:
        return json.load(f)


def normalize_name(name: str) -> str:
    """Normalize a name for deduplication matching."""
    return name.strip().lower().replace('\u2019', "'").replace('\u2018', "'")


# ============================================================
# Spell Merge
# ============================================================

def merge_spells():
    """Merge PSRD spells (detailed) with aonprd spell index (comprehensive)."""
    print("\n=== Merging Spells ===")

    psrd_spells = load_json('spells.json')
    aonprd_spells = load_json('aonprd_spells.json')

    # Index PSRD spells by normalized name
    psrd_by_name: dict[str, dict] = {}
    for s in psrd_spells:
        key = normalize_name(s['name'])
        psrd_by_name[key] = s

    merged: list[dict] = []
    added_from_aonprd = 0

    # Start with all PSRD spells (they have full details)
    for s in psrd_spells:
        # Add aonprd URL if available
        key = normalize_name(s['name'])
        s['url'] = None
        merged.append(s)

    psrd_keys = set(psrd_by_name.keys())

    # Add aonprd-only spells as index entries (name + url + brief description)
    for a in aonprd_spells:
        key = normalize_name(a['name'])
        if key not in psrd_keys:
            # Create a minimal spell entry from aonprd index data
            spell = {
                'name': a['name'],
                'school': '',
                'source': '',
                'class_levels': [],
                'subschool': None,
                'descriptors': [],
                'casting_time': '',
                'components': '',
                'range': '',
                'target': None,
                'area': None,
                'effect': None,
                'duration': '',
                'saving_throw': '',
                'spell_resistance': '',
                'description': a.get('description', ''),
                'url': f"https://aonprd.com/{a['url']}" if a.get('url') else None,
            }
            merged.append(spell)
            added_from_aonprd += 1

    # Update PSRD spells with aonprd URLs
    aonprd_by_name = {normalize_name(a['name']): a for a in aonprd_spells}
    for s in merged:
        key = normalize_name(s['name'])
        if key in aonprd_by_name and not s.get('url'):
            a = aonprd_by_name[key]
            s['url'] = f"https://aonprd.com/{a['url']}" if a.get('url') else None

    print(f"  PSRD spells: {len(psrd_spells)}")
    print(f"  aonprd spells: {len(aonprd_spells)}")
    print(f"  Added from aonprd: {added_from_aonprd}")
    print(f"  Total merged: {len(merged)}")

    return merged


# ============================================================
# Feat Merge
# ============================================================

def merge_feats():
    """Merge PSRD feats with aonprd feat index."""
    print("\n=== Merging Feats ===")

    psrd_feats = load_json('feats.json')
    aonprd_feats = load_json('aonprd_feats.json')

    psrd_by_name: dict[str, dict] = {}
    for f in psrd_feats:
        key = normalize_name(f['name'])
        psrd_by_name[key] = f

    merged: list[dict] = []
    added_from_aonprd = 0

    # Start with PSRD feats
    for f in psrd_feats:
        f['url'] = None
        merged.append(f)

    psrd_keys = set(psrd_by_name.keys())

    # Add aonprd-only feats
    for a in aonprd_feats:
        key = normalize_name(a['name'])
        if key not in psrd_keys:
            feat = {
                'name': a['name'],
                'source': '',
                'types': [a.get('category', 'General')],
                'prerequisites': a.get('prerequisites', ''),
                'benefit': a.get('description', ''),
                'normal': None,
                'special': None,
                'url': f"https://aonprd.com/{a['url']}" if a.get('url') else None,
            }
            merged.append(feat)
            added_from_aonprd += 1

    # Update PSRD feats with aonprd URLs
    aonprd_by_name = {normalize_name(a['name']): a for a in aonprd_feats}
    for f in merged:
        key = normalize_name(f['name'])
        if key in aonprd_by_name and not f.get('url'):
            a = aonprd_by_name[key]
            f['url'] = f"https://aonprd.com/{a['url']}" if a.get('url') else None

    print(f"  PSRD feats: {len(psrd_feats)}")
    print(f"  aonprd feats: {len(aonprd_feats)}")
    print(f"  Added from aonprd: {added_from_aonprd}")
    print(f"  Total merged: {len(merged)}")

    return merged


# ============================================================
# Archetype Compatibility
# ============================================================

def normalize_replaces(text: str) -> list[str]:
    """Normalize a 'replaces' summary into a list of feature names.

    Splits on ';' then ',' while handling 'and' connectors.
    Strips ordinal level prefixes like '1st-level', '3rd-level'.
    """
    if not text or not text.strip():
        return []

    features = []
    # Split on semicolons first
    for part in text.split(';'):
        # Split on commas
        sub_parts = part.split(',')
        for sub in sub_parts:
            # Split on " and " to handle "trap sense and uncanny dodge"
            and_parts = re.split(r'\s+and\s+', sub)
            for item in and_parts:
                item = item.strip()
                if not item:
                    continue
                # Strip ordinal level prefixes: "1st-level ", "3rd-level ", "2nd-", "4th-level "
                item = re.sub(r'^\d+(?:st|nd|rd|th)(?:-level)?\s*[-–]?\s*', '', item)
                # Lowercase and normalize whitespace
                item = re.sub(r'\s+', ' ', item).strip().lower()
                if item:
                    features.append(item)

    return features


# ============================================================
# Archetype Merge
# ============================================================

def merge_archetypes():
    """
    Merge PSRD archetypes (with parsed features) with aonprd archetypes
    (with explicit Replaces column).
    """
    print("\n=== Merging Archetypes ===")

    psrd_archetypes = load_json('archetypes.json')
    aonprd_archetypes = load_json('aonprd_archetypes.json')

    # Index PSRD by (base_class, name)
    psrd_by_key: dict[tuple[str, str], dict] = {}
    for a in psrd_archetypes:
        key = (normalize_name(a['base_class']), normalize_name(a['name']))
        psrd_by_key[key] = a

    # Index aonprd by (base_class, name)
    aonprd_by_key: dict[tuple[str, str], dict] = {}
    for a in aonprd_archetypes:
        key = (normalize_name(a['base_class']), normalize_name(a['name']))
        aonprd_by_key[key] = a

    merged: list[dict] = []
    enriched_count = 0
    added_from_aonprd = 0

    # Process PSRD archetypes, enriching with aonprd "Replaces" data
    for a in psrd_archetypes:
        key = (normalize_name(a['base_class']), normalize_name(a['name']))
        aonprd_match = aonprd_by_key.get(key)

        if aonprd_match:
            # Use aonprd's explicit "Replaces" text as authoritative
            a['replaces_summary'] = aonprd_match.get('replaces', '')
            a['url'] = (f"https://aonprd.com/{aonprd_match['url']}"
                       if aonprd_match.get('url') else None)
            a['replaced_features'] = normalize_replaces(a['replaces_summary'])
            if aonprd_match.get('replaces'):
                enriched_count += 1
        else:
            a['replaces_summary'] = ''
            a['url'] = None
            # For PSRD-only archetypes, build replaced_features from modifications
            features = []
            for mod in a.get('modifications', []):
                if mod.get('type') == 'replace' and mod.get('replaces'):
                    features.extend(normalize_replaces(mod['replaces']))
            a['replaced_features'] = features

        merged.append(a)

    psrd_keys = set(psrd_by_key.keys())

    # Add aonprd-only archetypes (minimal data — name, class, replaces)
    for a in aonprd_archetypes:
        key = (normalize_name(a['base_class']), normalize_name(a['name']))
        if key not in psrd_keys:
            replaces_summary = a.get('replaces', '')
            archetype = {
                'name': a['name'],
                'base_class': a['base_class'],
                'source': '',
                'description': a.get('summary', ''),
                'modifications': [],
                'replaces_summary': replaces_summary,
                'replaced_features': normalize_replaces(replaces_summary),
                'url': f"https://aonprd.com/{a['url']}" if a.get('url') else None,
            }
            merged.append(archetype)
            added_from_aonprd += 1

    with_features = sum(1 for a in merged if a.get('replaced_features'))
    print(f"  PSRD archetypes: {len(psrd_archetypes)}")
    print(f"  aonprd archetypes: {len(aonprd_archetypes)}")
    print(f"  Enriched with Replaces data: {enriched_count}")
    print(f"  Added from aonprd: {added_from_aonprd}")
    print(f"  With replaced_features: {with_features}")
    print(f"  Total merged: {len(merged)}")

    return merged


# ============================================================
# Main
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Merging PSRD + aonprd Data")

    spells = merge_spells()
    with open(os.path.join(OUTPUT_DIR, 'merged_spells.json'), 'w') as f:
        json.dump(spells, f, indent=2, ensure_ascii=False)
    print(f"  Saved merged_spells.json")

    feats = merge_feats()
    with open(os.path.join(OUTPUT_DIR, 'merged_feats.json'), 'w') as f:
        json.dump(feats, f, indent=2, ensure_ascii=False)
    print(f"  Saved merged_feats.json")

    archetypes = merge_archetypes()
    with open(os.path.join(OUTPUT_DIR, 'merged_archetypes.json'), 'w') as f:
        json.dump(archetypes, f, indent=2, ensure_ascii=False)
    print(f"  Saved merged_archetypes.json")

    # Final summary
    print("\n=== FINAL DATA SUMMARY ===")
    print(f"  Skills:     {len(load_json('skills.json'))}")
    print(f"  Races:      {len(load_json('races.json'))}")
    print(f"  Classes:    {len(load_json('classes.json'))}")
    print(f"  Archetypes: {len(archetypes)} (merged)")
    print(f"  Spells:     {len(spells)} (merged)")
    print(f"  Feats:      {len(feats)} (merged)")
    print(f"  Items:      {len(load_json('items.json'))}")

    total_size = 0
    for fname in os.listdir(OUTPUT_DIR):
        fpath = os.path.join(OUTPUT_DIR, fname)
        total_size += os.path.getsize(fpath)
    print(f"\n  Total output size: {total_size / 1024 / 1024:.1f} MB")


if __name__ == '__main__':
    main()
