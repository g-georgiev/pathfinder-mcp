"""
Parse seed character Google Sheets HTML exports into uniform JSON.

Handles all three seed characters:
  - Nettle (L3 Oracle/Sorcerer gestalt)
  - Roland (L13 Musket Master/Witch Hunter gestalt)
  - Amura (L20 Shifter/Rogue gestalt, Mythic T10)

Usage:
    python3 src/seed_parse.py           # Parse all characters
    python3 src/seed_parse.py Nettle    # Parse one character
"""

import os
import sys
import json
import re
import urllib.parse
from html.parser import HTMLParser


SEED_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'seed')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')


# ============================================================
# HTML Grid Parser
# ============================================================

class Cell:
    """A single cell in the parsed grid."""
    __slots__ = ('text', 'href')

    def __init__(self, text='', href=None):
        self.text = text
        self.href = href

    def __repr__(self):
        if self.href:
            return f'Cell({self.text!r}, href=...)'
        return f'Cell({self.text!r})'

    def __bool__(self):
        return bool(self.text.strip())


class GridParser(HTMLParser):
    """Parse a Google Sheets HTML export into a 2D grid of Cells."""

    def __init__(self):
        super().__init__()
        self.grid: list[list[Cell]] = []
        self.current_row: list[Cell] = []
        self.current_cell: Cell | None = None
        self.in_tbody = False
        self.in_td = False
        self.in_th = False
        self.in_a = False
        self.current_href = ''

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag = tag.lower()

        if tag == 'tbody':
            self.in_tbody = True
        elif tag == 'tr' and self.in_tbody:
            self.current_row = []
        elif tag == 'th' and self.in_tbody:
            self.in_th = True
        elif tag == 'td' and self.in_tbody:
            self.in_td = True
            self.current_cell = Cell()
        elif tag == 'a' and self.in_td:
            self.in_a = True
            self.current_href = attrs_dict.get('href', '')
        elif tag == 'br' and self.in_td:
            if self.current_cell is not None:
                self.current_cell.text += '\n'

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == 'tbody':
            self.in_tbody = False
        elif tag == 'th':
            self.in_th = False
        elif tag == 'td' and self.in_td:
            self.in_td = False
            if self.current_cell is not None:
                self.current_cell.text = self.current_cell.text.strip()
                self.current_row.append(self.current_cell)
            self.current_cell = None
        elif tag == 'a' and self.in_a:
            self.in_a = False
            if self.current_cell is not None and self.current_href and not self.current_cell.href:
                self.current_cell.href = self.current_href
            self.current_href = ''
        elif tag == 'tr' and self.in_tbody:
            self.grid.append(self.current_row)
            self.current_row = []

    def handle_data(self, data):
        if self.in_td and self.current_cell is not None:
            self.current_cell.text += data

    def handle_entityref(self, name):
        entities = {
            'amp': '&', 'lt': '<', 'gt': '>', 'quot': '"',
            'mdash': '\u2014', 'ndash': '\u2013', 'apos': "'",
            'nbsp': ' ',
        }
        char = entities.get(name, f'&{name};')
        if self.in_td and self.current_cell is not None:
            self.current_cell.text += char

    def handle_charref(self, name):
        try:
            char = chr(int(name[1:], 16) if name.startswith('x') else int(name))
        except (ValueError, OverflowError):
            char = f'&#{name};'
        if self.in_td and self.current_cell is not None:
            self.current_cell.text += char


def parse_grid(html: str) -> list[list[Cell]]:
    parser = GridParser()
    parser.feed(html)
    return parser.grid


# ============================================================
# Grid Utilities
# ============================================================

def ct(grid, r, c, default='') -> str:
    """Get cell text at (row, col) with bounds checking."""
    if 0 <= r < len(grid) and 0 <= c < len(grid[r]):
        return grid[r][c].text.strip()
    return default


def ch(grid, r, c) -> str | None:
    """Get cell href at (row, col)."""
    if 0 <= r < len(grid) and 0 <= c < len(grid[r]):
        return grid[r][c].href
    return None


def find_label(grid, label: str) -> tuple[int, int] | None:
    """Find (row, col) of first cell matching label (case-insensitive)."""
    target = label.strip().lower()
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell.text.strip().lower() == target:
                return (r, c)
    return None


def find_labels(grid, label: str) -> list[tuple[int, int]]:
    """Find all (row, col) of cells matching label (case-insensitive)."""
    target = label.strip().lower()
    results = []
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell.text.strip().lower() == target:
                results.append((r, c))
    return results


def find_label_startswith(grid, prefix: str) -> list[tuple[int, int]]:
    """Find all cells starting with prefix."""
    target = prefix.strip().lower()
    results = []
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell.text.strip().lower().startswith(target):
                results.append((r, c))
    return results


def parse_int(s: str, default: int = 0) -> int:
    """Parse integer from string, stripping non-numeric chars."""
    s = s.strip().replace(',', '')
    m = re.match(r'^[+-]?\d+', s)
    return int(m.group()) if m else default


def parse_float(s: str, default: float = 0.0) -> float:
    s = s.strip().replace(',', '')
    m = re.match(r'^[+-]?\d+\.?\d*', s)
    return float(m.group()) if m else default


def collect_right(grid, r: int, start_c: int) -> list[Cell]:
    """Collect non-empty cells to the right of (r, start_c)."""
    if r >= len(grid):
        return []
    return [cell for cell in grid[r][start_c:] if cell.text.strip()]


def collect_down(grid, start_r: int, c: int) -> list[Cell]:
    """Collect non-empty cells downward from (start_r, c)."""
    results = []
    for r in range(start_r, len(grid)):
        if c < len(grid[r]) and grid[r][c].text.strip():
            results.append(grid[r][c])
        else:
            break
    return results


# ============================================================
# Bio Extraction
# ============================================================

def extract_bio(grid) -> dict:
    """Extract identity data from a Bio page grid."""
    bio = {}

    # Map of label -> output field name
    label_map = {
        'name': 'name',
        'alignment': 'alignment',
        'race': 'race',
        'gender': 'gender',
        'age': 'age',
        'level': 'level',
        'diety': 'deity',
        'deity': 'deity',
        'size': 'size',
        'height': 'height',
        'wight': 'weight',  # typo in source sheets
        'weight': 'weight',
        'eye color': 'eye_color',
        'hair color': 'hair_color',
        'mythic 1': 'mythic_1',
        'mythic 2': 'mythic_2',
        'tier': 'tier',
    }

    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            key = cell.text.strip().lower().rstrip(':')
            if key not in label_map:
                continue

            field = label_map[key]
            val_c = c + 1

            if field in ('class_1', 'class_2'):
                continue  # handled below

            if val_c < len(row):
                bio[field] = row[val_c].text.strip()

    # Extract classes with archetypes
    for class_label in ('class 1', 'class 2'):
        pos = find_label(grid, class_label)
        if not pos:
            continue

        r, c = pos
        slot = 1 if '1' in class_label else 2
        class_entry = {'slot': slot, 'name': '', 'archetypes': []}

        # Collect all non-empty cells to the right
        archetype_urls = []
        for vc in range(c + 1, len(grid[r])):
            txt = ct(grid, r, vc)
            href = ch(grid, r, vc)
            if not txt:
                continue
            if href and 'ArchetypeDisplay' in href:
                class_entry['archetypes'].append(txt)
                archetype_urls.append(href)
            elif href and 'ClassDisplay' in href:
                class_entry['name'] = txt
            elif not class_entry['name']:
                class_entry['name'] = txt

        # Infer class name from archetype URLs if not found directly
        # e.g. "Oracle%20Dual-Cursed%20Oracle" → "Oracle"
        if not class_entry['name'] and archetype_urls:
            for url in archetype_urls:
                fixed_name = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('FixedName', [''])[0]
                if fixed_name:
                    # First word before the archetype name is typically the class
                    class_entry['name'] = fixed_name.split()[0]
                    break

        bio.setdefault('classes', []).append(class_entry)

    # Extract domains (Amura)
    pos = find_label(grid, 'domains:')
    if not pos:
        pos = find_label(grid, 'domains')
    if pos:
        r, c = pos
        domains = []
        # First domain might be on the same row
        first = ct(grid, r, c + 1)
        if first:
            domains.append(first)
        # Remaining domains in rows below in the same column
        for dr in range(r + 1, len(grid)):
            val = ct(grid, dr, c + 1)
            if val:
                domains.append(val)
            else:
                break
        if domains:
            bio['domains'] = domains

    # Build mythic if present
    if bio.get('mythic_1') or bio.get('mythic_2'):
        paths = []
        if bio.get('mythic_1'):
            paths.append(bio.pop('mythic_1'))
        if bio.get('mythic_2'):
            paths.append(bio.pop('mythic_2'))
        bio['mythic'] = {
            'paths': paths,
            'tier': parse_int(bio.pop('tier', '0')),
        }
    else:
        bio.pop('mythic_1', None)
        bio.pop('mythic_2', None)
        bio.pop('tier', None)
        bio['mythic'] = None

    # Normalize numeric fields
    for f in ('age', 'level'):
        if f in bio:
            bio[f] = parse_int(bio[f])

    return bio


# ============================================================
# Stats Extraction
# ============================================================

ABILITY_NAMES = {
    'strength': 'STR', 'str': 'STR',
    'dexterity': 'DEX', 'dex': 'DEX',
    'constitution': 'CON', 'con': 'CON',
    'intelligence': 'INT', 'int': 'INT',
    'wisdom': 'WIS', 'wis': 'WIS',
    'charisma': 'CHA', 'cha': 'CHA',
}


def extract_stats(grid) -> dict:
    """Extract stats from a Stats page grid."""
    stats = {}

    # --- Level (Nettle has it on the Stats page, not Bio) ---
    pos = find_label(grid, 'level')
    if pos:
        r, c = pos
        # Value might be to the right (possibly several cols over)
        for vc in range(c + 1, min(c + 5, len(grid[r]) if r < len(grid) else 0)):
            val = ct(grid, r, vc)
            if val and re.match(r'^\d+$', val):
                stats['level'] = int(val)
                break

    # --- Abilities ---
    abilities = {}
    abilities_pos = find_label(grid, 'abilities')
    if abilities_pos:
        a_row, a_col = abilities_pos
        # Parse header row to find column positions dynamically
        col_map = {}  # field -> column offset from a_col
        for vc in range(a_col + 1, min(a_col + 8, len(grid[a_row]))):
            h = ct(grid, a_row, vc).lower().replace('/', '')
            if 'base' in h:
                col_map['base'] = vc
            elif 'race' in h or 'level' in h:
                col_map['racial'] = vc
            elif 'item' in h:
                col_map['item'] = vc
            elif 'total' in h:
                col_map['total'] = vc
            elif 'mod' in h:
                col_map['modifier'] = vc

        for dr in range(a_row + 1, min(a_row + 8, len(grid))):
            name_text = ct(grid, dr, a_col).lower()
            if name_text not in ABILITY_NAMES:
                continue
            abbr = ABILITY_NAMES[name_text]
            abilities[abbr] = {
                'base': parse_int(ct(grid, dr, col_map['base'])) if 'base' in col_map else 0,
                'racial': parse_int(ct(grid, dr, col_map['racial'])) if 'racial' in col_map else 0,
                'item': parse_int(ct(grid, dr, col_map['item'])) if 'item' in col_map else 0,
                'total': parse_int(ct(grid, dr, col_map['total'])) if 'total' in col_map else 0,
                'modifier': parse_int(ct(grid, dr, col_map['modifier'])) if 'modifier' in col_map else 0,
            }
    stats['abilities'] = abilities

    # --- AC ---
    ac_pos = find_label(grid, 'ac')
    if ac_pos:
        r, c = ac_pos
        # Parse formula: 10 + dex + armor + misc = TOTAL
        # Find '=' and take the number after it
        ac_total = 0
        found_eq = False
        for vc in range(c + 1, min(c + 12, len(grid[r]) if r < len(grid) else 0)):
            val = ct(grid, r, vc).strip()
            if '=' in val:
                found_eq = True
                continue
            if found_eq and re.match(r'^[+-]?\d+$', val):
                ac_total = int(val)
                break
        stats['ac'] = ac_total

        # Check for "Other bonuses" on next rows
        ac_bonuses = []
        for dr in range(r + 1, min(r + 5, len(grid))):
            txt = ct(grid, dr, c)
            if 'other bonus' in txt.lower() or 'bonus' in txt.lower():
                bonus_val = ct(grid, dr, c + 1)
                bonus_desc = ct(grid, dr, c + 2)
                if bonus_val:
                    ac_bonuses.append({'value': parse_int(bonus_val), 'source': bonus_desc})
        if ac_bonuses:
            stats['ac_bonuses'] = ac_bonuses

    # --- HP ---
    hp_pos = find_label(grid, 'hp')
    if hp_pos:
        r, c = hp_pos
        stats['hp'] = parse_int(ct(grid, r, c + 1))

    # --- Hit Die ---
    hd_pos = find_label(grid, 'hit die')
    if not hd_pos:
        hd_pos = find_label(grid, 'hit die')
    if hd_pos:
        r, c = hd_pos
        stats['hit_die'] = parse_int(ct(grid, r, c + 1))

    # --- Speed ---
    speed_pos = find_label(grid, 'speed')
    if speed_pos:
        r, c = speed_pos
        # Try vertical layout first: rows below with Walk/Fly/Swim/Climb/Burrow
        SPEED_MODES = ('walk', 'fly', 'swim', 'climb', 'burrow', 'land')
        entries = []
        for dr in range(r + 1, min(r + 6, len(grid))):
            mode = ct(grid, dr, c)
            if mode and mode.lower() in SPEED_MODES:
                # Value might be 1-3 columns to the right (sometimes empty cols between)
                val = ''
                for offset in (1, 2, 3):
                    v = ct(grid, dr, c + offset)
                    if v and 'ft' in v.lower():
                        val = v
                        break
                if val:
                    entries.append(f"{mode} {val}")
            elif entries:
                break  # end of speed section
        if entries:
            stats['speed'] = ', '.join(entries)
        else:
            # Horizontal layout: find "Xft" value, then include adjacent descriptors
            speed_parts = []
            found_ft = False
            for vc in range(c + 1, min(c + 6, len(grid[r]) if r < len(grid) else 0)):
                val = ct(grid, r, vc)
                if not val:
                    if found_ft:
                        break  # stop after ft value + any descriptors
                    continue
                if 'ft' in val.lower():
                    speed_parts.append(val)
                    found_ft = True
                elif found_ft:
                    # Descriptor after the ft value (e.g. "Land AND SWIM")
                    speed_parts.append(val)
                    break  # only take one descriptor
            stats['speed'] = ' '.join(speed_parts) if speed_parts else ''

    # --- BAB ---
    bab_pos = find_label(grid, 'bab')
    if bab_pos:
        r, c = bab_pos
        # Look for "Main" label on the next row
        bab_values = []
        for dr in range(r + 1, min(r + 3, len(grid))):
            row_text = ct(grid, dr, c)
            if row_text.lower() == 'main':
                val = ct(grid, dr, c + 1)
                if val:
                    # Could be "13/8/3" format
                    bab_values = [parse_int(x) for x in val.split('/')]
                break
        if not bab_values:
            # Try right of BAB label
            val = ct(grid, r, c + 1)
            if val:
                bab_values = [parse_int(x) for x in val.split('/')]
        stats['bab'] = bab_values

    # --- Saves ---
    saves_pos = find_label(grid, 'saves')
    if saves_pos:
        r, c = saves_pos
        saves = {}
        for dr in range(r + 1, min(r + 5, len(grid))):
            save_name = ct(grid, dr, c).lower()
            if save_name in ('fortitude', 'fort'):
                key = 'fort'
            elif save_name in ('reflex', 'ref'):
                key = 'ref'
            elif save_name in ('will',):
                key = 'will'
            else:
                continue
            base = parse_int(ct(grid, dr, c + 1))
            ability = parse_int(ct(grid, dr, c + 2))
            item = parse_int(ct(grid, dr, c + 3))
            total = parse_int(ct(grid, dr, c + 4))
            saves[key] = {
                'base': base, 'ability': ability, 'item': item, 'total': total,
            }
        stats['saves'] = saves

    # --- CMB / CMD / Initiative ---
    # These all use formula format: label ... num + num = TOTAL
    for stat_name in ('cmb', 'cmd', 'initiative'):
        pos = find_label(grid, stat_name)
        if not pos:
            continue
        r, c = pos
        # Find the number after '='
        found_eq = False
        for vc in range(c + 1, min(c + 12, len(grid[r]) if r < len(grid) else 0)):
            val = ct(grid, r, vc).strip()
            if '=' in val:
                found_eq = True
                continue
            if found_eq and re.match(r'^[+-]?\d+$', val):
                stats[stat_name] = int(val)
                break

    # --- Skills ---
    skills = extract_skills(grid)
    if skills:
        stats['skills'] = skills

    # --- Attacks ---
    attacks = extract_attacks(grid)
    if attacks:
        stats['attacks'] = attacks

    return stats


def extract_skills(grid) -> list[dict]:
    """Extract skills from the stats grid."""
    # Find the "Skill" header
    skill_pos = find_label(grid, 'skill')
    if not skill_pos:
        return []

    r, c = skill_pos
    # Header: Skill | Ability | Base | Ranks | Bonuses | Total
    skills = []
    for dr in range(r + 1, len(grid)):
        name = ct(grid, dr, c)
        if not name:
            # Could be end of skills section or a gap - check next row
            next_name = ct(grid, dr + 1, c) if dr + 1 < len(grid) else ''
            if not next_name:
                break
            continue

        # Skip if it looks like a section header (bold/underline markers)
        if name.lower() in ('total', 'total used', ''):
            continue

        ability = ct(grid, dr, c + 1)
        base = parse_int(ct(grid, dr, c + 2))
        ranks = parse_int(ct(grid, dr, c + 3))
        bonuses = parse_int(ct(grid, dr, c + 4))
        total = parse_int(ct(grid, dr, c + 5))

        # Check for notes further right
        notes = ct(grid, dr, c + 7) or ct(grid, dr, c + 8) or ''

        skill = {
            'name': name,
            'ability': ability.upper() if ability else '',
            'total': total,
            'ranks': ranks,
        }
        if notes:
            skill['notes'] = notes
        skills.append(skill)

    return skills


def extract_attacks(grid) -> list[dict]:
    """Extract attack entries from the stats grid."""
    atk_pos = find_label(grid, 'attacks')
    if not atk_pos:
        return []

    r, c = atk_pos
    # Header: Attacks | AB | DMG | | Critical | Type
    attacks = []
    for dr in range(r + 1, len(grid)):
        name = ct(grid, dr, c)
        if not name:
            next_name = ct(grid, dr + 1, c) if dr + 1 < len(grid) else ''
            if not next_name:
                break
            continue

        ab = ct(grid, dr, c + 1)
        dmg = ct(grid, dr, c + 2)
        # col c+3 might be empty (spacer)
        crit = ct(grid, dr, c + 4) or ct(grid, dr, c + 3)
        atk_type = ct(grid, dr, c + 5) or ct(grid, dr, c + 4)

        if not ab and not dmg:
            continue

        attacks.append({
            'name': name,
            'attack_bonus': ab,
            'damage': dmg,
            'critical': crit,
            'type': atk_type,
        })

    return attacks


# ============================================================
# Feats & Traits Extraction
# ============================================================

def extract_feats_and_traits(grid) -> dict:
    """Extract feats, traits, racial traits, and languages from a feats/traits grid."""
    result = {
        'racial_traits': [],
        'languages': [],
        'character_traits': [],
        'feats': [],
        'class_features': [],
    }

    # Identify sections by header labels
    section = None
    for r, row in enumerate(grid):
        # Check for section headers in col B (index 1) or col A (index 0)
        for header_col in (1, 0):
            header = ct(grid, r, header_col).lower().rstrip(':')
            if header in ('racial traits', 'racial'):
                section = 'racial_traits'
                break
            elif header == 'languages':
                section = 'languages'
                # Languages value is in the next column
                langs = ct(grid, r, header_col + 1)
                if langs:
                    result['languages'] = [l.strip() for l in langs.split(',')]
                section = None
                break
            elif header in ('traits', 'character traits'):
                section = 'traits'
                break
            elif header in ('feats',):
                section = 'feats'
                break
            elif header in ('evolutions',):
                section = 'evolutions'
                break
        else:
            # No header found - process data rows based on current section
            if section == 'racial_traits':
                name = ct(grid, r, 1)
                if name and name.lower() not in ('racial traits', 'physical traits:', ''):
                    short_desc = ct(grid, r, 2)
                    long_desc = ct(grid, r, 3)
                    result['racial_traits'].append({
                        'name': name,
                        'effect': short_desc,
                        'description': long_desc,
                    })

            elif section == 'traits':
                name = ct(grid, r, 1)
                href = ch(grid, r, 1)
                if name:
                    detail = ct(grid, r, 2)
                    entry = {'name': name, 'detail': detail}
                    if href:
                        entry['url'] = href
                    result['character_traits'].append(entry)

            elif section == 'feats':
                # Feat rows: col A = level tag, col B = name, col C = description
                level_tag = ct(grid, r, 0)
                name = ct(grid, r, 1)
                href = ch(grid, r, 1)
                desc = ct(grid, r, 2)
                long_desc = ct(grid, r, 3)

                if not name:
                    continue

                entry = {
                    'level': level_tag,
                    'name': name,
                    'effect': desc,
                }
                if href:
                    entry['url'] = href
                if long_desc:
                    entry['description'] = long_desc
                result['feats'].append(entry)

    return result


# ============================================================
# Extended Feats (Roland/Amura style - combined feats + class features)
# ============================================================

def extract_feats_extended(grid) -> dict:
    """
    Extract from Roland/Amura-style "Feats & Special abilities" pages.
    Columns: col0=level tag, col1=name, col2=type, col3=short effect, col4=long desc
    Sections are separated by header rows.
    """
    result = {
        'racial_traits': [],
        'languages': [],
        'character_traits': [],
        'feats': [],
        'class_features': [],
        'evolutions': [],
    }

    section = None

    for r in range(len(grid)):
        # Detect section headers - check col 1 for standalone labels
        header_text = ct(grid, r, 1).lower().rstrip(':').strip()
        col0 = ct(grid, r, 0)
        col2 = ct(grid, r, 2)

        # A section header is typically a standalone label in col 1 with no data in col 2+
        # or a very short entry that signals a new section
        is_header = False

        if header_text in ('racial traits', 'racial'):
            section = 'racial_traits'
            is_header = True
        elif header_text == 'languages':
            langs = ct(grid, r, 2)
            if langs:
                result['languages'] = [l.strip() for l in langs.split(',')]
            is_header = True
        elif header_text in ('traits', 'character traits'):
            section = 'traits'
            is_header = True
        elif header_text in ('feat', 'feats'):
            section = 'feats'
            is_header = True
        elif header_text in ('evolutions',):
            section = 'evolutions'
            is_header = True
        elif header_text in ('special abilities', 'rogue talents', 'class features',
                              'class abilities', 'ninja tricks', 'rage powers',
                              'magus arcana', 'discoveries', 'hexes',
                              'slayer talents', 'vigilante talents'):
            section = 'class_features'
            is_header = True

        if is_header:
            continue

        # Check for class features section transition
        # These are long descriptions that act as both header and content
        CLASS_KEYWORDS = ('nimble (ex)', 'gun training', 'politics inquisition',
                          'spell sage', 'knowledgeable defense', 'spell scent',
                          'judgment', 'stern gaze', 'cunning initiative',
                          'solo tactics', 'teamwork feat', 'bane (su)', 'bane:',
                          'greater bane', 'domain:', 'domain powers',
                          'blessing of', 'invoke deity', 'hermean potential',
                          'community', 'luck', 'war', 'binding ties', 'unity',
                          'bit of luck', 'good fortune', 'seize the initiative',
                          'weapon master')

        if header_text and not col0 and any(kw in header_text for kw in CLASS_KEYWORDS):
            # This is a class feature line - add to class features regardless of section
            href = ch(grid, r, 1)
            entry = {
                'name': ct(grid, r, 1),
                'level': '',
                'type': col2 if col2 else '',
                'effect': ct(grid, r, 3) if len(grid[r]) > 3 else '',
            }
            if href:
                entry['url'] = href
            if len(grid[r]) > 4 and ct(grid, r, 4):
                entry['description'] = ct(grid, r, 4)
            result['class_features'].append(entry)
            continue

        # Process data rows
        level_tag = col0
        name = ct(grid, r, 1)
        type_val = ct(grid, r, 2)
        effect = ct(grid, r, 3)
        long_desc = ct(grid, r, 4) if len(grid[r]) > 4 else ''

        if not name:
            continue

        # Skip column header rows in any section (e.g. "Name | Type | Effect (short) | ...")
        if name.lower() in ('name', 'feat name', 'feat'):
            continue

        if section == 'feats':
            href = ch(grid, r, 1)
            entry = {
                'level': level_tag,
                'name': name,
                'type': type_val,
                'effect': effect,
            }
            if href:
                entry['url'] = href
            if long_desc:
                entry['description'] = long_desc
            result['feats'].append(entry)

        elif section == 'traits':
            href = ch(grid, r, 1)
            # Entries with type "Racial" belong in racial_traits
            if type_val and type_val.lower() == 'racial':
                result['racial_traits'].append({
                    'name': name,
                    'effect': effect,
                    'description': long_desc or '',
                })
            else:
                entry = {'name': name, 'detail': type_val}
                if href:
                    entry['url'] = href
                if effect:
                    entry['effect'] = effect
                result['character_traits'].append(entry)

        elif section == 'racial_traits':
            result['racial_traits'].append({
                'name': name,
                'effect': type_val,
                'description': effect or '',
            })

        elif section == 'evolutions':
            result['evolutions'].append({
                'name': name,
                'level': level_tag,
                'effect': type_val,
                'description': effect or '',
            })

        elif section == 'class_features':
            href = ch(grid, r, 1)
            entry = {
                'name': name,
                'level': level_tag,
                'type': type_val,
                'effect': effect,
            }
            if href:
                entry['url'] = href
            if long_desc:
                entry['description'] = long_desc
            result['class_features'].append(entry)

        elif section is None:
            # Unclassified rows with level tags → likely class features
            if level_tag or type_val:
                href = ch(grid, r, 1)
                entry = {
                    'name': name,
                    'level': level_tag,
                    'type': type_val,
                    'effect': effect,
                }
                if href:
                    entry['url'] = href
                if long_desc:
                    entry['description'] = long_desc
                result['class_features'].append(entry)

    return result


# ============================================================
# Class Abilities Extraction (Nettle-style separate page)
# ============================================================

CLASS_NAMES = frozenset((
    'oracle', 'sorcerer', 'wizard', 'cleric', 'bard',
    'fighter', 'ranger', 'paladin', 'barbarian',
    'monk', 'rogue', 'druid', 'inquisitor',
    'shifter', 'gunslinger', 'witch', 'alchemist',
    'warpriest', 'bloodrager', 'investigator',
))


def extract_class_abilities(grid) -> list[dict]:
    """Extract class abilities from a dedicated Class abilities page."""
    features = []
    current_class = ''

    for r, row in enumerate(grid):
        # Check for class header in col 0 or col 1 (class names appear standalone)
        for hc in (0, 1):
            h = ct(grid, r, hc).strip()
            if h and h.lower() in CLASS_NAMES:
                # Verify it's a standalone header (no data in other cols)
                other = ct(grid, r, hc + 1) if hc + 1 < len(row) else ''
                if not other:
                    current_class = h
                    break
        else:
            # Not a class header - process as data row
            name = ct(grid, r, 1)
            if not name:
                continue

            level_tag = ct(grid, r, 0)
            detail = ct(grid, r, 2)
            long_desc = ct(grid, r, 3)
            href = ch(grid, r, 1) or ch(grid, r, 2)

            entry = {
                'class': current_class,
                'name': name,
                'level': level_tag,
                'effect': detail,
            }
            if href:
                entry['url'] = href
            if long_desc:
                entry['description'] = long_desc
            features.append(entry)

    return features


# ============================================================
# Spell Extraction
# ============================================================

def extract_spells(grid, class_hint: str = '') -> dict:
    """
    Extract spells from a spell page grid.

    Returns: {
        'class': str,
        'base_dc': int,
        'spells_per_day': {level: count},
        'spells_known': {level: count},
        'spell_list': [{level, name, source, notes, url}]
    }
    """
    result = {
        'class': class_hint,
        'base_dc': 0,
        'spells_per_day': {},
        'spells_known': {},
        'spell_list': [],
    }

    # Find base DC
    dc_pos = find_label(grid, 'base dc')
    if not dc_pos:
        dc_pos = find_label(grid, 'dc')
    if dc_pos:
        r, c = dc_pos
        result['base_dc'] = parse_int(ct(grid, r, c + 1))

    # Find spells per day / spells known tables
    # Format A (Nettle): header row with level numbers (0, 1, 2, ...) near label row
    # Format B (Roland): "1st", "2nd", "3rd" headers with "Per day:", "Class:", "Bonus:" rows

    # Ordinal-to-number mapping
    ORDINAL_MAP = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4, '5th': 5,
                   '6th': 6, '7th': 7, '8th': 8, '9th': 9}

    def _parse_level_header(val):
        """Parse a level header: '0'-'9' or '1st'-'9th' → int, else None."""
        if re.match(r'^\d$', val):
            return int(val)
        return ORDINAL_MAP.get(val.lower())

    def _count_level_headers(row_idx, start_c):
        """Count valid level headers in a row. Returns (count, has_ordinal)."""
        count = 0
        has_ordinal = False
        if row_idx < 0 or row_idx >= len(grid):
            return 0, False
        for vc in range(start_c, min(start_c + 12, len(grid[row_idx]))):
            val = ct(grid, row_idx, vc)
            if not val:
                continue
            lvl = _parse_level_header(val)
            if lvl is not None:
                count += 1
                if val.lower() in ORDINAL_MAP:
                    has_ordinal = True
        return count, has_ordinal

    def _find_spell_table(label_names, key):
        for table_name in label_names:
            pos = find_label(grid, table_name)
            if not pos:
                continue
            r, c = pos

            # Find header row: search up to 5 rows above and 2 below
            # Prefer rows with ordinal headers (1st, 2nd) or many digit headers
            best_row = None
            best_score = 0
            for check_r in range(max(0, r - 5), min(len(grid), r + 3)):
                count, has_ordinal = _count_level_headers(check_r, c + 1)
                # Score: ordinals get bonus; require at least 3 headers to avoid false positives
                score = count + (10 if has_ordinal else 0)
                if count >= 3 and score > best_score:
                    best_score = score
                    best_row = check_r

            if best_row is None:
                continue

            header_row = best_row
            # Values row: same row as label if header is above, else row below header
            val_row = r if header_row < r else header_row + 1
            if val_row >= len(grid):
                continue

            table = {}
            for vc in range(c + 1, min(c + 12, len(grid[header_row]))):
                level_str = ct(grid, header_row, vc)
                value_str = ct(grid, val_row, vc)
                level = _parse_level_header(level_str) if level_str else None
                if level is not None:
                    if value_str == '-' or value_str.lower() == 'unlimited':
                        table[level] = -1
                    elif value_str:
                        table[level] = parse_int(value_str)
            if table:
                result[key] = table
                return True
        return False

    _find_spell_table(['spells per day', 'spells / day', 'per day', 'per day:'], 'spells_per_day')
    _find_spell_table(['spells known'], 'spells_known')

    # Detect item/domain spell-like abilities format (Amura):
    # Rows have: name | "X / day" | optional link  - no spell level numbers
    # Check if the grid has "/ day" patterns but no level-number columns
    has_per_day_entries = False
    has_level_numbers = False
    for r_check in range(len(grid)):
        for c_check in range(min(4, len(grid[r_check]))):
            val = ct(grid, r_check, c_check)
            if val and '/ day' in val:
                has_per_day_entries = True
            if val and re.match(r'^[0-9]$', val) and c_check <= 1:
                # Digit in first 2 columns likely a spell level
                has_level_numbers = True
    if has_per_day_entries and not has_level_numbers:
        # Item/domain SLA format
        current_section = 'items'
        for r in range(len(grid)):
            name = ct(grid, r, 1)
            if not name:
                continue
            freq = ct(grid, r, 2)
            # Detect domain/section headers (no frequency)
            if name and not freq and not ct(grid, r, 3):
                if 'domain' in name.lower() or 'subdomain' in name.lower():
                    current_section = name
                    continue
                elif name.lower() in ('from items', 'spells'):
                    current_section = name
                    continue
                elif name.lower() == 'familiar':
                    current_section = '_skip'
                    continue
            if not freq or current_section == '_skip':
                continue
            href = ch(grid, r, 1) or ch(grid, r, 2) or ch(grid, r, 3)
            # If name is a URL, extract spell name
            if name.startswith('http'):
                name = name.rstrip('/').rsplit('/', 1)[-1].replace('-', ' ').title()
            entry = {
                'level': -1,  # SLAs don't have standard levels
                'name': name,
                'source': current_section,
                'notes': freq,
            }
            if href:
                entry['url'] = href
            result['spell_list'].append(entry)
        return result

    # Extract spell list
    # Look for rows where col A or B has a spell level (0, 1, 2, ...) and subsequent
    # rows have spell names
    current_level = -1
    for r in range(len(grid)):
        # Check if this row has a level indicator
        for c in range(min(3, len(grid[r]))):
            val = ct(grid, r, c)
            if val and re.match(r'^(Level\s+)?\d+$', val, re.IGNORECASE):
                level_match = re.search(r'\d+', val)
                if level_match:
                    new_level = int(level_match.group())
                    if 0 <= new_level <= 9:
                        current_level = new_level

        if current_level < 0:
            continue

        # Look for spell names - they typically have links or are in the name column
        # Spell rows usually have: level_indicator | name | summary | source
        # or just name with a link
        for c in range(len(grid[r])):
            cell = grid[r][c]
            href = cell.href
            name = cell.text.strip()

            if not name:
                continue

            # Skip non-spell cells (numbers, operators, headers)
            if re.match(r'^[\d+= ]+$', name):
                continue
            if name.lower() in ('level', 'spells per day', 'spells known',
                                 'spells / day', 'base dc', 'dc',
                                 'unlimited', '0', '1', '2', '3', '4', '5',
                                 '6', '7', '8', '9', '+'):
                continue

            # If it has a SpellDisplay link, it's definitely a spell
            if href and ('SpellDisplay' in href or 'pfsrd.com' in href):
                # If text is a URL, extract spell name from it
                spell_name = name
                if spell_name.startswith('http'):
                    # e.g. http://www.d20pfsrd.com/magic/all-spells/r/resist-energy
                    last_seg = spell_name.rstrip('/').rsplit('/', 1)[-1]
                    spell_name = last_seg.replace('-', ' ').title()
                source = ct(grid, r, c + 1) if c + 1 < len(grid[r]) else ''
                notes = ct(grid, r, c + 2) if c + 2 < len(grid[r]) else ''
                result['spell_list'].append({
                    'level': current_level,
                    'name': spell_name,
                    'source': source,
                    'notes': notes,
                    'url': href,
                })
            # Also detect bare URLs without href (text IS a spell URL)
            elif not href and name.startswith('http') and ('pfsrd.com' in name or 'aonprd.com' in name):
                last_seg = name.rstrip('/').rsplit('/', 1)[-1]
                spell_name = last_seg.replace('-', ' ').title()
                result['spell_list'].append({
                    'level': current_level,
                    'name': spell_name,
                    'source': '',
                    'notes': '',
                    'url': name,
                })

    # Strip 0-value entries from spells_per_day and spells_known
    result['spells_per_day'] = {k: v for k, v in result['spells_per_day'].items() if v != 0}
    result['spells_known'] = {k: v for k, v in result['spells_known'].items() if v != 0}

    return result


# ============================================================
# Character Discovery & Assembly
# ============================================================

def discover_characters() -> dict[str, str]:
    """Find all character sheet directories in the seed folder."""
    chars = {}
    if not os.path.isdir(SEED_DIR):
        print(f"Seed directory not found: {SEED_DIR}")
        return chars

    for entry in sorted(os.listdir(SEED_DIR)):
        path = os.path.join(SEED_DIR, entry)
        if os.path.isdir(path) and 'sheet' in entry.lower():
            # Extract character name from folder name
            name = entry.replace("'s sheet alt", '').replace("'s sheet", '')
            name = name.replace("\u2019s sheet alt", '').replace("\u2019s sheet", '')
            name = name.strip()
            chars[name] = path

    return chars


def find_page(char_dir: str, patterns: list[str]) -> str | None:
    """Find a file in char_dir matching any of the given patterns (case-insensitive)."""
    for fname in os.listdir(char_dir):
        if not fname.endswith('.html'):
            continue
        lower = fname.lower()
        for pattern in patterns:
            if pattern.lower() in lower:
                return os.path.join(char_dir, fname)
    return None


def load_grid(filepath: str) -> list[list[Cell]]:
    """Load and parse an HTML file into a grid."""
    with open(filepath, encoding='utf-8') as f:
        html = f.read()
    return parse_grid(html)


def parse_character(name: str, char_dir: str) -> dict:
    """Parse all pages for a character into a uniform JSON structure."""
    print(f"\n{'='*60}")
    print(f"Parsing: {name}")
    print(f"  Directory: {char_dir}")

    character = {
        'name': name,
        'alignment': '',
        'race': '',
        'gender': '',
        'age': 0,
        'level': 0,
        'deity': '',
        'size': '',
        'height': '',
        'weight': '',
        'eye_color': '',
        'hair_color': '',
        'classes': [],
        'mythic': None,
        'domains': [],
        'stat_blocks': [],
        'feats': [],
        'character_traits': [],
        'racial_traits': [],
        'languages': [],
        'class_features': [],
        'spellcasting': [],
    }

    # --- Bio ---
    bio_file = find_page(char_dir, ['bio'])
    if bio_file:
        print(f"  Bio: {os.path.basename(bio_file)}")
        grid = load_grid(bio_file)
        bio = extract_bio(grid)
        # Merge bio into character
        for key in ('name', 'alignment', 'race', 'gender', 'age', 'level',
                     'deity', 'size', 'height', 'weight', 'eye_color', 'hair_color',
                     'classes', 'mythic', 'domains'):
            if key in bio and bio[key]:
                character[key] = bio[key]

    # --- Stats ---
    stat_files = []
    for fname in sorted(os.listdir(char_dir)):
        if fname.endswith('.html') and 'stat' in fname.lower():
            stat_files.append(os.path.join(char_dir, fname))

    for stat_file in stat_files:
        fname = os.path.basename(stat_file)
        print(f"  Stats: {fname}")
        grid = load_grid(stat_file)
        stats = extract_stats(grid)

        # Determine form name from filename
        form_match = re.search(r'\(([^)]+)\)', fname)
        form = form_match.group(1) if form_match else 'default'

        stats['form'] = form

        # If level wasn't in bio, get it from stats
        if not character['level'] and stats.get('level'):
            character['level'] = stats.pop('level')
        else:
            stats.pop('level', None)

        character['stat_blocks'].append(stats)

    # --- Feats & Traits ---
    feats_file = find_page(char_dir, ['feats', 'traits and feats'])
    if feats_file:
        fname = os.path.basename(feats_file)
        print(f"  Feats: {fname}")
        grid = load_grid(feats_file)

        # Detect format: Nettle-style (simple cols B-D) vs Roland/Amura-style (cols A-F)
        # Heuristic: if we find "Evolutions" or many columns with data, use extended parser
        has_evolutions = find_label(grid, 'evolutions') is not None
        col_count = max(len(row) for row in grid) if grid else 0

        if has_evolutions or col_count > 5:
            ft = extract_feats_extended(grid)
        else:
            ft = extract_feats_and_traits(grid)

        for key in ('racial_traits', 'languages', 'character_traits', 'feats', 'class_features'):
            if ft.get(key):
                character[key] = ft[key]

    # --- Class Abilities (Nettle-style separate page) ---
    abilities_file = find_page(char_dir, ['class abilities'])
    if abilities_file:
        print(f"  Class Abilities: {os.path.basename(abilities_file)}")
        grid = load_grid(abilities_file)
        features = extract_class_abilities(grid)
        character['class_features'].extend(features)

    # --- Spells ---
    spell_files = []
    for fname in sorted(os.listdir(char_dir)):
        if fname.endswith('.html') and 'spell' in fname.lower():
            spell_files.append(os.path.join(char_dir, fname))

    for spell_file in spell_files:
        fname = os.path.basename(spell_file)
        print(f"  Spells: {fname}")

        # Infer class from filename
        class_hint = ''
        lower = fname.lower()
        if 'oracle' in lower:
            class_hint = 'Oracle'
        elif 'sorcerer' in lower:
            class_hint = 'Sorcerer'
        elif 'wizard' in lower:
            class_hint = 'Wizard'
        elif 'cleric' in lower:
            class_hint = 'Cleric'

        grid = load_grid(spell_file)
        spells = extract_spells(grid, class_hint=class_hint)
        character['spellcasting'].append(spells)

    # Try to infer spellcasting class from character's classes when not set
    SPELLCASTING_CLASSES = {
        'oracle', 'sorcerer', 'wizard', 'cleric', 'druid', 'bard', 'paladin',
        'ranger', 'inquisitor', 'witch', 'magus', 'summoner', 'alchemist',
        'warpriest', 'bloodrager', 'investigator', 'shaman', 'skald',
        'arcanist', 'hunter', 'medium', 'mesmerist', 'occultist',
        'psychic', 'spiritualist',
    }
    # Also map archetypes/variants to their base class spell list
    CLASS_SPELL_MAP = {
        'witch hunter': 'Inquisitor',
        'musket master': 'Gunslinger',
        'holy beast shifter': 'Shifter',
        'counterfeit mage unchained rogue': 'Rogue',
    }
    char_classes = character.get('classes', [])
    for sp in character.get('spellcasting', []):
        if sp.get('class'):
            continue
        # Try to find a spellcasting class among character's classes
        for cls in char_classes:
            cls_name = cls.get('name', '')
            mapped = CLASS_SPELL_MAP.get(cls_name.lower(), cls_name)
            if mapped.lower() in SPELLCASTING_CLASSES:
                sp['class'] = mapped
                break

    # Clean up empty fields
    character = {k: v for k, v in character.items() if v is not None}

    return character


# ============================================================
# Main
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check for specific character filter
    filter_name = sys.argv[1] if len(sys.argv) > 1 else None

    characters = discover_characters()
    if not characters:
        print(f"No character sheets found in {SEED_DIR}")
        return

    print(f"Found {len(characters)} character(s): {', '.join(characters.keys())}")

    results = []
    for name, char_dir in characters.items():
        if filter_name and filter_name.lower() not in name.lower():
            continue
        char = parse_character(name, char_dir)
        results.append(char)

        # Save individual character file
        out_path = os.path.join(OUTPUT_DIR, f'seed_{name.lower()}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(char, f, indent=2, ensure_ascii=False)
        print(f"  Saved {out_path}")

    # Save combined file
    if results:
        combined_path = os.path.join(OUTPUT_DIR, 'seed_characters.json')
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSaved combined: {combined_path}")

    # Summary
    print(f"\n{'='*60}")
    print("SEED CHARACTER PARSE SUMMARY")
    print(f"{'='*60}")
    for char in results:
        stat_forms = [sb.get('form', '?') for sb in char.get('stat_blocks', [])]
        print(f"  {char.get('name', '?')}: L{char.get('level', '?')} "
              f"{char.get('race', '?')}, "
              f"{len(char.get('classes', []))} classes, "
              f"{len(char.get('stat_blocks', []))} stat block(s) ({', '.join(stat_forms)}), "
              f"{len(char.get('feats', []))} feats, "
              f"{len(char.get('spellcasting', []))} spell lists")


if __name__ == '__main__':
    main()
