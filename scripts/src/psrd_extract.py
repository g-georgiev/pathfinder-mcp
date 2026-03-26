"""
Extract and normalize game data from PSRD-Data SQLite databases.

Uses index.db as the master cross-book index and pulls detailed data
from individual book databases as needed.

Output: JSON files in data/output/ for classes, archetypes, spells, feats,
items, races, and skills.
"""

import os
import sys
import re
import sqlite3
import json
from dataclasses import asdict
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(__file__))
from models import (
    BaseClass, ClassProgression, ClassFeature, SpellCasting, PrestigeRequirement,
    Archetype, ArchetypeModification, ArchetypeFeature,
    Race, RacialTrait, AlternateRacialTrait,
    Skill, Spell, SpellClassLevel, Feat, ParsedPrerequisite, MagicItem,
    Equipment, WeaponStats, ArmorStats,
    Domain, Subdomain, Bloodline, OracleMystery, WitchPatron, DomainSpellEntry,
    save_json
)

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'psrd')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')

# Cache for opened database connections
_db_cache: dict[str, sqlite3.Connection] = {}


def get_db(db_name: str) -> sqlite3.Connection:
    """Get a connection to a book database, with caching."""
    if db_name not in _db_cache:
        path = os.path.join(RAW_DIR, db_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Database not found: {path}")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        _db_cache[db_name] = conn
    return _db_cache[db_name]


def get_index_db() -> sqlite3.Connection:
    return get_db('index.db')


# ============================================================
# HTML Table Parser
# ============================================================

class ProgressionTableParser(HTMLParser):
    """Parse a class progression HTML table into structured rows."""

    def __init__(self):
        super().__init__()
        self.rows: list[list[str]] = []
        self.headers: list[str] = []
        self.current_row: list[str] = []
        self.current_cell = ''
        self.in_cell = False
        self.in_header = False
        self.in_thead = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == 'thead':
            self.in_thead = True
        elif tag == 'tr':
            self.current_row = []
        elif tag in ('td', 'th'):
            self.in_cell = True
            self.in_header = tag == 'th'
            self.current_cell = ''
        elif tag == 'br' and self.in_cell:
            self.current_cell += ', '
        elif tag == 'sup':
            pass  # skip footnote markers

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'thead':
            self.in_thead = False
        elif tag in ('td', 'th'):
            self.in_cell = False
            cell_text = self.current_cell.strip()
            self.current_row.append(cell_text)
        elif tag == 'tr':
            if self.current_row:
                if self.in_thead:
                    # Header row - only store the first header row
                    if not self.headers:
                        self.headers = self.current_row
                else:
                    self.rows.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data

    def handle_entityref(self, name):
        entities = {'mdash': '—', 'ndash': '–', 'times': '×', 'amp': '&', 'lt': '<', 'gt': '>'}
        if self.in_cell:
            self.current_cell += entities.get(name, f'&{name};')

    def handle_charref(self, name):
        if self.in_cell:
            try:
                self.current_cell += chr(int(name))
            except ValueError:
                self.current_cell += f'&#{name};'


def parse_progression_table(html: str) -> tuple[list[str], list[list[str]]]:
    """Parse a class progression table HTML, returning (headers, rows)."""
    parser = ProgressionTableParser()
    parser.feed(html)
    return parser.headers, parser.rows


def parse_bab(bab_str: str) -> int:
    """Parse BAB string like '+6/+1' into the highest BAB value."""
    bab_str = bab_str.strip().replace('–', '-').replace('—', '-')
    if not bab_str or bab_str == '-':
        return 0
    parts = bab_str.split('/')
    try:
        return int(parts[0].replace('+', ''))
    except ValueError:
        return 0


def parse_save(save_str: str) -> int:
    """Parse save string like '+2' into integer."""
    save_str = save_str.strip().replace('–', '-').replace('—', '-')
    if not save_str or save_str == '-':
        return 0
    try:
        return int(save_str.replace('+', ''))
    except ValueError:
        return 0


def parse_spells_per_day(row: list[str], start_col: int) -> list[int | None]:
    """Parse spells-per-day columns from a progression table row."""
    result = []
    for cell in row[start_col:]:
        cell = cell.strip().replace('—', '').replace('–', '').replace('-', '').strip()
        if cell == '' or cell == '\u2014':
            result.append(None)
        else:
            try:
                result.append(int(cell))
            except ValueError:
                result.append(None)
    return result


# ============================================================
# Text extraction from HTML
# ============================================================

class SimpleTextExtractor(HTMLParser):
    """Extract plain text from HTML body content."""

    def __init__(self):
        super().__init__()
        self.pieces: list[str] = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ('script', 'style', 'sup'):
            self.skip = True
        elif tag.lower() in ('br', 'p', 'div', 'li'):
            self.pieces.append(' ')

    def handle_endtag(self, tag):
        if tag.lower() in ('script', 'style', 'sup'):
            self.skip = False
        elif tag.lower() in ('p', 'div'):
            self.pieces.append(' ')

    def handle_data(self, data):
        if not self.skip:
            self.pieces.append(data)

    def handle_entityref(self, name):
        entities = {'mdash': '—', 'ndash': '–', 'times': '×', 'amp': '&'}
        if not self.skip:
            self.pieces.append(entities.get(name, f'&{name};'))

    def handle_charref(self, name):
        if not self.skip:
            try:
                self.pieces.append(chr(int(name)))
            except ValueError:
                pass

    def get_text(self) -> str:
        text = ''.join(self.pieces)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


def html_to_text(html: str | None) -> str:
    """Convert HTML to plain text."""
    if not html:
        return ''
    ext = SimpleTextExtractor()
    ext.feed(html)
    return ext.get_text()


# ============================================================
# Class Extraction
# ============================================================

def extract_classes() -> list[BaseClass]:
    """Extract all base classes from PSRD data."""
    print("\n=== Extracting Classes ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database, subtype
        FROM central_index
        WHERE type = 'class'
        ORDER BY name
    """)
    class_entries = cur.fetchall()
    print(f"  Found {len(class_entries)} class entries in index")

    classes = []
    for entry in class_entries:
        db_name = entry['database']
        section_id = entry['section_id']
        class_name = entry['name']
        source = entry['source']
        subtype = entry['subtype']  # core, base, hybrid, prestige, npc, unchained

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            print(f"  SKIP {class_name} - missing database {db_name}")
            continue

        dcur = db.cursor()

        # Get class details (hit_die, alignment)
        dcur.execute("SELECT * FROM class_details WHERE section_id = ?", (section_id,))
        details = dcur.fetchone()
        if not details:
            print(f"  SKIP {class_name} - no class_details")
            continue

        hit_die_str = details['hit_die'] or 'd8'
        hit_die_match = re.search(r'd(\d+)', hit_die_str)
        hit_die = int(hit_die_match.group(1)) if hit_die_match else 8

        alignment = details['alignment'] or 'Any'
        # Trim long alignment descriptions
        if len(alignment) > 50:
            # Find first sentence
            period_idx = alignment.find('.')
            if period_idx > 0:
                alignment = alignment[:period_idx + 1]

        # Get body description
        dcur.execute("SELECT body, description FROM sections WHERE section_id = ?", (section_id,))
        main_section = dcur.fetchone()
        description = html_to_text(main_section['body']) if main_section else ''
        if len(description) > 500:
            description = description[:500] + '...'

        # Get ALL descendants to find skill ranks, class skills, progression table, class features
        dcur.execute("SELECT lft, rgt FROM sections WHERE section_id = ?", (section_id,))
        bounds = dcur.fetchone()
        if not bounds:
            continue

        # Query all descendants (not just direct children)
        dcur.execute("""
            SELECT section_id, name, type, subtype, body, description, parent_id
            FROM sections
            WHERE lft > ? AND rgt < ?
            ORDER BY lft
        """, (bounds['lft'], bounds['rgt']))
        all_descendants = dcur.fetchall()

        skill_ranks = 0
        class_skills: list[str] = []
        progression: list[ClassProgression] = []
        class_features: list[ClassFeature] = []
        spells_per_day_data: list[list[int | None]] = []
        has_spells = False
        class_features_section_id = None

        for desc in all_descendants:
            desc_name = (desc['name'] or '').strip()
            desc_body = desc['body'] or ''
            desc_type = desc['type'] or ''

            if desc_name == 'Skill Ranks per Level':
                m = re.search(r'(\d+)', html_to_text(desc_body))
                if m:
                    skill_ranks = int(m.group(1))

            elif desc_name == 'Class Skills' and desc_type == 'section':
                text = html_to_text(desc_body)
                skills_raw = re.findall(r'([A-Z][\w\s]+?)\s*\(', text)
                class_skills = [s.strip() for s in skills_raw if s.strip()]

            elif desc_name == 'Class Features' and desc_type == 'section':
                class_features_section_id = desc['section_id']

            elif desc_type == 'ability' and class_features_section_id and desc['parent_id'] == class_features_section_id:
                # Direct child ability of Class Features section
                feat_name = desc_name
                feat_body = html_to_text(desc_body)
                if len(feat_body) > 1000:
                    feat_body = feat_body[:1000] + '...'

                dcur.execute("SELECT ability_type FROM ability_types WHERE section_id = ?",
                            (desc['section_id'],))
                atype_row = dcur.fetchone()
                ability_type = None
                if atype_row:
                    atype = atype_row['ability_type']
                    if 'Extraordinary' in atype:
                        ability_type = 'Ex'
                    elif 'Supernatural' in atype:
                        ability_type = 'Su'
                    elif 'Spell-Like' in atype:
                        ability_type = 'Sp'

                class_features.append(ClassFeature(
                    name=feat_name,
                    level=0,
                    description=feat_body,
                    ability_type=ability_type
                ))

        # Find the progression table among descendants
        # Strategy: prefer table with class name in title, then any table with BAB columns
        table_section = None
        candidate_tables = [
            desc for desc in all_descendants
            if desc['type'] == 'table' and desc['body'] and '<table' in desc['body']
        ]

        # Pass 1: table named after the class (e.g., "Table: Barbarian")
        for t in candidate_tables:
            t_name = (t['name'] or '').strip()
            if class_name.lower() in t_name.lower():
                table_section = t
                break

        # Pass 2: table containing progression columns (Level + Base Attack Bonus)
        if not table_section:
            for t in candidate_tables:
                body_lower = t['body'].lower()
                if 'base attack' in body_lower and 'level' in body_lower:
                    table_section = t
                    break

        if table_section and table_section['body']:
            headers, rows = parse_progression_table(table_section['body'])

            # Determine column indices from headers
            bab_col = None
            fort_col = None
            ref_col = None
            will_col = None
            special_col = None
            spd_start_col = None  # Spells per day start column

            for i, h in enumerate(headers):
                h_lower = h.lower().strip()
                if 'attack' in h_lower or 'bab' in h_lower:
                    bab_col = i
                elif 'fort' in h_lower:
                    fort_col = i
                elif 'ref' in h_lower:
                    ref_col = i
                elif 'will' in h_lower:
                    will_col = i
                elif 'special' in h_lower:
                    special_col = i
                elif h_lower in ('0', '0th', '1st', '2nd', '3rd') and spd_start_col is None:
                    spd_start_col = i
                    has_spells = True
                elif 'spells per day' in h_lower or 'spells known' in h_lower:
                    # Merged header like "Spells per Day" spanning multiple columns.
                    # Actual spell data starts at the next column index in data rows.
                    # But since this header occupies one slot, spd data starts at i
                    # in data rows (which have more columns than headers).
                    spd_start_col = i
                    has_spells = True

            for row in rows:
                if len(row) < 5:
                    continue
                # Parse level from "1st", "2nd", etc.
                level_str = row[0].strip()
                level_match = re.match(r'(\d+)', level_str)
                if not level_match:
                    continue
                level = int(level_match.group(1))

                bab = parse_bab(row[bab_col]) if bab_col is not None and bab_col < len(row) else 0
                fort = parse_save(row[fort_col]) if fort_col is not None and fort_col < len(row) else 0
                ref_save = parse_save(row[ref_col]) if ref_col is not None and ref_col < len(row) else 0
                will_save = parse_save(row[will_col]) if will_col is not None and will_col < len(row) else 0

                special = []
                if special_col is not None and special_col < len(row):
                    raw_special = row[special_col].strip()
                    if raw_special and raw_special != '—' and raw_special != '-':
                        special = [s.strip() for s in raw_special.split(',') if s.strip()]

                progression.append(ClassProgression(
                    level=level,
                    bab=bab,
                    fort=fort,
                    ref=ref_save,
                    will=will_save,
                    special=special
                ))

                if has_spells and spd_start_col is not None:
                    spd = parse_spells_per_day(row, spd_start_col)
                    spells_per_day_data.append(spd)

        # Determine spellcasting info
        spellcasting = None
        if has_spells and spells_per_day_data:
            # Determine casting type from class name / source heuristics
            arcane_classes = {'Wizard', 'Sorcerer', 'Bard', 'Magus', 'Witch', 'Arcanist',
                              'Bloodrager', 'Skald', 'Summoner'}
            divine_classes = {'Cleric', 'Druid', 'Paladin', 'Ranger', 'Inquisitor',
                              'Oracle', 'Warpriest', 'Shaman', 'Hunter'}
            psychic_classes = {'Psychic', 'Mesmerist', 'Occultist', 'Spiritualist', 'Kineticist'}

            if class_name in arcane_classes:
                cast_type = 'arcane'
            elif class_name in divine_classes:
                cast_type = 'divine'
            elif class_name in psychic_classes:
                cast_type = 'psychic'
            elif class_name == 'Alchemist':
                cast_type = 'alchemist'
            else:
                cast_type = 'arcane'  # default

            spontaneous_classes = {'Sorcerer', 'Bard', 'Oracle', 'Bloodrager', 'Skald',
                                   'Summoner', 'Arcanist', 'Psychic', 'Mesmerist'}
            is_spontaneous = class_name in spontaneous_classes

            cha_casters = {'Sorcerer', 'Bard', 'Oracle', 'Paladin', 'Bloodrager',
                           'Skald', 'Summoner'}
            wis_casters = {'Cleric', 'Druid', 'Ranger', 'Inquisitor', 'Warpriest',
                           'Shaman', 'Hunter'}
            int_casters = {'Wizard', 'Witch', 'Magus', 'Alchemist', 'Arcanist',
                           'Investigator'}

            if class_name in cha_casters:
                casting_ability = 'CHA'
            elif class_name in wis_casters:
                casting_ability = 'WIS'
            elif class_name in int_casters:
                casting_ability = 'INT'
            else:
                casting_ability = 'CHA'

            spellcasting = SpellCasting(
                type=cast_type,
                spontaneous=is_spontaneous,
                casting_ability=casting_ability,
                spells_per_day=spells_per_day_data
            )

        # Resolve feature levels from progression table special column
        feature_name_to_level: dict[str, int] = {}
        for prog in progression:
            for s in prog.special:
                s_clean = re.sub(r'\s*\(.*?\)', '', s).strip().lower()
                if s_clean not in feature_name_to_level:
                    feature_name_to_level[s_clean] = prog.level

        for feat in class_features:
            feat_clean = feat.name.strip().lower()
            if feat_clean in feature_name_to_level:
                feat.level = feature_name_to_level[feat_clean]

        # Parse prestige class requirements
        requirements: list[PrestigeRequirement] = []
        if subtype == 'prestige':
            requirements = parse_prestige_requirements(all_descendants, section_id, db)

        cls = BaseClass(
            name=class_name,
            source=source,
            description=description,
            hit_die=hit_die,
            skill_ranks_per_level=skill_ranks,
            class_skills=class_skills,
            progression=progression,
            class_features=class_features,
            spellcasting=spellcasting,
            alignment=alignment,
            requirements=requirements,
        )
        classes.append(cls)
        feat_count = len(class_features)
        prog_count = len(progression)
        req_str = f' REQS={len(requirements)}' if requirements else ''
        print(f"  {class_name} ({source}) hd=d{hit_die} skills={skill_ranks} prog={prog_count} feats={feat_count}{' SPELLS' if spellcasting else ''}{req_str}")

    return classes


# ============================================================
# Archetype Extraction
# ============================================================

def extract_archetypes() -> list[Archetype]:
    """Extract all archetypes from PSRD data."""
    print("\n=== Extracting Archetypes ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database, subtype, parent_name
        FROM central_index
        WHERE type = 'class_archetype'
        ORDER BY parent_name, name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} archetype entries in index")

    archetypes = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']
        arch_name = entry['name']
        source = entry['source']
        base_class = entry['parent_name'] or entry['subtype'] or ''

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()

        # Get archetype body
        dcur.execute("SELECT body, description FROM sections WHERE section_id = ?", (section_id,))
        section = dcur.fetchone()
        if not section:
            continue

        description = html_to_text(section['body'])
        if len(description) > 500:
            description = description[:500] + '...'

        # Get children (the modified abilities)
        dcur.execute("SELECT lft, rgt FROM sections WHERE section_id = ?", (section_id,))
        bounds = dcur.fetchone()
        if not bounds:
            archetypes.append(Archetype(
                name=arch_name, base_class=base_class,
                source=source, description=description, modifications=[]
            ))
            continue

        dcur.execute("""
            SELECT section_id, name, type, subtype, body
            FROM sections
            WHERE lft > ? AND rgt < ? AND parent_id = ?
            ORDER BY lft
        """, (bounds['lft'], bounds['rgt'], section_id))
        children = dcur.fetchall()

        modifications: list[ArchetypeModification] = []
        for child in children:
            child_name = child['name'] or ''
            child_body = html_to_text(child['body'])
            if not child_name or not child_body:
                continue

            # Try to detect "replaces" or "alters" from the body text
            replaces = None
            mod_type = 'add'

            # Common patterns: "This replaces X", "This ability replaces X",
            # "This modifies X", "This alters X"
            replace_match = re.search(
                r'This (?:ability |class feature )?replaces?\s+(.+?)(?:\.|$)',
                child_body, re.IGNORECASE
            )
            alter_match = re.search(
                r'This (?:ability |class feature )?(?:alters?|modifies?)\s+(.+?)(?:\.|$)',
                child_body, re.IGNORECASE
            )

            if replace_match:
                replaces = replace_match.group(1).strip()
                # Clean up: remove trailing HTML artifacts
                replaces = re.sub(r'\s+', ' ', replaces).strip()
                if len(replaces) > 100:
                    replaces = replaces[:100]
                mod_type = 'replace'
            elif alter_match:
                replaces = alter_match.group(1).strip()
                replaces = re.sub(r'\s+', ' ', replaces).strip()
                if len(replaces) > 100:
                    replaces = replaces[:100]
                mod_type = 'alter'

            if len(child_body) > 1000:
                child_body = child_body[:1000] + '...'

            # Detect ability type
            dcur.execute("SELECT ability_type FROM ability_types WHERE section_id = ?",
                        (child['section_id'],))
            atype_row = dcur.fetchone()
            ability_type = None
            if atype_row:
                atype = atype_row['ability_type']
                if 'Extraordinary' in atype:
                    ability_type = 'Ex'
                elif 'Supernatural' in atype:
                    ability_type = 'Su'
                elif 'Spell-Like' in atype:
                    ability_type = 'Sp'

            modifications.append(ArchetypeModification(
                type=mod_type,
                replaces=replaces,
                feature=ArchetypeFeature(
                    name=child_name,
                    description=child_body,
                    ability_type=ability_type
                )
            ))

        archetypes.append(Archetype(
            name=arch_name,
            base_class=base_class,
            source=source,
            description=description,
            modifications=modifications
        ))

    replace_count = sum(1 for a in archetypes for m in a.modifications if m.type == 'replace')
    alter_count = sum(1 for a in archetypes for m in a.modifications if m.type == 'alter')
    add_count = sum(1 for a in archetypes for m in a.modifications if m.type == 'add')
    print(f"  Extracted {len(archetypes)} archetypes "
          f"({replace_count} replacements, {alter_count} alterations, {add_count} additions)")
    return archetypes


# ============================================================
# Spell Extraction
# ============================================================

def extract_spells() -> list[Spell]:
    """Extract all spells using index.db's cross-book spell data."""
    print("\n=== Extracting Spells ===")
    idx = get_index_db()
    cur = idx.cursor()

    # Get all spells from central_index with their details
    cur.execute("""
        SELECT ci.index_id, ci.section_id, ci.name, ci.source, ci.database,
               ci.spell_school, ci.spell_subschool_text, ci.spell_descriptor_text,
               ci.spell_list_text, ci.spell_component_text, ci.description
        FROM central_index ci
        WHERE ci.type = 'spell'
        ORDER BY ci.name
    """)
    spell_entries = cur.fetchall()
    print(f"  Found {len(spell_entries)} spell entries in index")

    # Build class/level lookup from spell_list_index
    cur.execute("SELECT * FROM spell_list_index")
    spell_list_rows = cur.fetchall()
    spell_class_levels: dict[int, list[SpellClassLevel]] = {}
    for row in spell_list_rows:
        idx_id = row['index_id']
        if idx_id not in spell_class_levels:
            spell_class_levels[idx_id] = []
        spell_class_levels[idx_id].append(SpellClassLevel(
            class_name=row['class'],
            level=row['level']
        ))

    spells = []
    for entry in spell_entries:
        index_id = entry['index_id']
        db_name = entry['database']
        section_id = entry['section_id']

        # Get detailed spell info from book database
        casting_time = ''
        spell_range = ''
        duration = ''
        saving_throw = ''
        spell_resistance = ''
        components = entry['spell_component_text'] or ''
        target = None
        area = None
        effect = None
        description = entry['description'] or ''

        try:
            db = get_db(db_name)
            dcur = db.cursor()

            dcur.execute("SELECT * FROM spell_details WHERE section_id = ?", (section_id,))
            details = dcur.fetchone()
            if details:
                casting_time = details['casting_time'] or ''
                spell_range = details['range'] or ''
                duration = details['duration'] or ''
                saving_throw = details['saving_throw'] or ''
                spell_resistance = details['spell_resistance'] or ''
                components = details['component_text'] or components

            # Get spell effects (Target, Area, Effect)
            dcur.execute("SELECT name, description FROM spell_effects WHERE section_id = ?",
                        (section_id,))
            for eff in dcur.fetchall():
                eff_name = (eff['name'] or '').lower()
                eff_desc = eff['description'] or ''
                if 'target' in eff_name:
                    target = eff_desc
                elif 'area' in eff_name:
                    area = eff_desc
                elif 'effect' in eff_name:
                    effect = eff_desc

            # Get description from body if not already present
            if not description:
                dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
                body_row = dcur.fetchone()
                if body_row and body_row['body']:
                    description = html_to_text(body_row['body'])

        except FileNotFoundError:
            pass

        if len(description) > 500:
            description = description[:500] + '...'

        # Parse subschool and descriptors
        subschool = entry['spell_subschool_text']
        descriptors = []
        if entry['spell_descriptor_text']:
            descriptors = [d.strip() for d in entry['spell_descriptor_text'].split(',') if d.strip()]

        spell = Spell(
            name=entry['name'],
            school=entry['spell_school'] or '',
            source=entry['source'] or '',
            class_levels=spell_class_levels.get(index_id, []),
            subschool=subschool,
            descriptors=descriptors,
            casting_time=casting_time,
            components=components,
            range=spell_range,
            target=target,
            area=area,
            effect=effect,
            duration=duration,
            saving_throw=saving_throw,
            spell_resistance=spell_resistance,
            description=description,
        )
        spells.append(spell)

    print(f"  Extracted {len(spells)} spells, "
          f"{sum(1 for s in spells if s.class_levels)} with class/level data")
    return spells


# ============================================================
# Feat Extraction
# ============================================================

def split_prerequisites(text: str) -> list[str]:
    """Split prerequisite text on ',' and ';' while respecting parentheses."""
    tokens = []
    current = []
    depth = 0
    for ch in text:
        if ch == '(':
            depth += 1
            current.append(ch)
        elif ch == ')':
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch in (',', ';') and depth == 0:
            token = ''.join(current).strip()
            if token:
                tokens.append(token)
            current = []
        else:
            current.append(ch)
    token = ''.join(current).strip()
    if token:
        tokens.append(token)
    return tokens


def parse_feat_prerequisites(text: str) -> list[ParsedPrerequisite]:
    """Parse feat prerequisite text into structured prerequisites."""
    if not text or not text.strip():
        return []

    tokens = split_prerequisites(text)
    result = []

    for token in tokens:
        token = token.strip().rstrip('.')
        if not token:
            continue

        # Ability score: "Str 13", "Dex 15", etc.
        m = re.match(r'^(Str|Dex|Con|Int|Wis|Cha)\s+(\d+)$', token)
        if m:
            result.append(ParsedPrerequisite(
                type='ability', name=m.group(1), value=int(m.group(2))))
            continue

        # BAB: "base attack bonus +6"
        m = re.search(r'base attack bonus \+(\d+)', token, re.IGNORECASE)
        if m:
            result.append(ParsedPrerequisite(
                type='bab', value=int(m.group(1))))
            continue

        # Caster level: "caster level 5th"
        m = re.search(r'caster level (\d+)(?:st|nd|rd|th)?', token, re.IGNORECASE)
        if m:
            result.append(ParsedPrerequisite(
                type='caster_level', value=int(m.group(1))))
            continue

        # Skill ranks: "Knowledge (arcana) 5 ranks"
        m = re.match(r'(.+?)\s+(\d+)\s+ranks?', token, re.IGNORECASE)
        if m:
            result.append(ParsedPrerequisite(
                type='skill', name=m.group(1).strip(), value=int(m.group(2))))
            continue

        # Class level: "fighter level 4", "wizard level 5"
        m = re.match(r'(\w[\w\s]*?)\s+level\s+(\d+)(?:st|nd|rd|th)?', token, re.IGNORECASE)
        if m:
            result.append(ParsedPrerequisite(
                type='class_level', name=m.group(1).strip(), value=int(m.group(2))))
            continue

        # Class feature: "sneak attack class feature"
        m = re.match(r'(.+?)\s+class feature', token, re.IGNORECASE)
        if m:
            result.append(ParsedPrerequisite(
                type='class_feature', name=m.group(1).strip()))
            continue

        # Looks like a feat name (starts with uppercase, short)
        if re.match(r'^[A-Z]', token) and len(token) < 80 and ' or ' not in token.lower():
            result.append(ParsedPrerequisite(
                type='feat', name=token))
            continue

        # Fallback
        result.append(ParsedPrerequisite(
            type='special', detail=token))

    return result


def extract_feats() -> list[Feat]:
    """Extract all feats from PSRD data."""
    print("\n=== Extracting Feats ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database,
               feat_type_description, feat_prerequisites, description
        FROM central_index
        WHERE type = 'feat'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} feat entries in index")

    feats = []
    for entry in entries:
        # Parse feat types from description like "(Combat, Teamwork)"
        types: list[str] = []
        type_desc = entry['feat_type_description'] or ''
        type_matches = re.findall(r'(\w+)', type_desc)
        types = [t for t in type_matches if t.lower() not in ('and', 'or', 'the')]

        prerequisites = entry['feat_prerequisites'] or ''
        benefit = entry['description'] or ''

        # Get full benefit from book DB if description is short
        if len(benefit) < 50:
            db_name = entry['database']
            section_id = entry['section_id']
            try:
                db = get_db(db_name)
                dcur = db.cursor()
                dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
                row = dcur.fetchone()
                if row and row['body']:
                    benefit = html_to_text(row['body'])
            except FileNotFoundError:
                pass

        if len(benefit) > 500:
            benefit = benefit[:500] + '...'

        parsed_prereqs = parse_feat_prerequisites(prerequisites)

        feat = Feat(
            name=entry['name'],
            source=entry['source'] or '',
            types=types,
            prerequisites=prerequisites,
            benefit=benefit,
            parsed_prerequisites=parsed_prereqs,
        )
        feats.append(feat)

    parsed_count = sum(1 for f in feats if f.parsed_prerequisites)
    print(f"  Extracted {len(feats)} feats ({parsed_count} with parsed prerequisites)")
    return feats


# ============================================================
# Item Extraction
# ============================================================

def extract_items() -> list[MagicItem]:
    """Extract all items from PSRD data."""
    print("\n=== Extracting Items ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database, description, url
        FROM central_index
        WHERE type = 'item'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} item entries in index")

    items = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']
        description = entry['description'] or ''

        slot = None
        aura = None
        caster_level = None
        price = ''
        weight = None
        construction_req = None
        construction_cost = None
        category = 'other'

        try:
            db = get_db(db_name)
            dcur = db.cursor()

            # Get item details
            dcur.execute("SELECT * FROM item_details WHERE section_id = ?", (section_id,))
            details = dcur.fetchone()
            if details:
                aura = details['aura']
                slot = details['slot']
                price = details['price'] or ''
                weight = details['weight']
                cl_str = details['cl'] or ''
                cl_match = re.search(r'(\d+)', cl_str)
                if cl_match:
                    caster_level = int(cl_match.group(1))

            # Get construction info from item_misc
            dcur.execute("""
                SELECT field, value FROM item_misc
                WHERE section_id = ? AND subsection = 'Construction'
            """, (section_id,))
            for misc in dcur.fetchall():
                if misc['field'] == 'Requirements':
                    construction_req = misc['value']
                elif misc['field'] == 'Cost':
                    construction_cost = misc['value']

            # Get description from body
            if not description:
                dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
                row = dcur.fetchone()
                if row and row['body']:
                    description = html_to_text(row['body'])

        except FileNotFoundError:
            pass

        if len(description) > 500:
            description = description[:500] + '...'

        # Determine category from URL path
        url = entry['url'] or ''
        url_lower = url.lower()
        if 'wondrous' in url_lower or 'wonderous' in url_lower:
            category = 'wondrous'
        elif 'weapon' in url_lower:
            category = 'weapon'
        elif 'armor' in url_lower or 'shield' in url_lower:
            category = 'armor'
        elif 'ring' in url_lower:
            category = 'ring'
        elif 'rod' in url_lower:
            category = 'rod'
        elif 'staff' in url_lower and 'staves' in url_lower:
            category = 'staff'
        elif 'potion' in url_lower:
            category = 'potion'
        elif 'scroll' in url_lower:
            category = 'scroll'
        elif 'wand' in url_lower:
            category = 'wand'
        elif 'artifact' in url_lower:
            category = 'artifact'
        elif aura:  # has magical aura = magic item
            category = 'wondrous'

        # Derive slot from URL path if not directly stored
        if not slot and 'wondrous' in url_lower:
            slot_match = re.search(
                r'/(Belt|Body|Chest|Eyes|Feet|Hands|Head|Headband|Neck|'
                r'Ring|Shield|Shoulders|Wrists|Slotless)/',
                url, re.IGNORECASE
            )
            if slot_match:
                slot = slot_match.group(1).lower()

        item = MagicItem(
            name=entry['name'],
            source=entry['source'] or '',
            category=category,
            price=price,
            slot=slot,
            aura=aura,
            caster_level=caster_level,
            weight=weight,
            description=description,
            construction_requirements=construction_req,
            construction_cost=construction_cost,
        )
        items.append(item)

    print(f"  Extracted {len(items)} items")
    cat_counts = {}
    for item in items:
        cat_counts[item.category] = cat_counts.get(item.category, 0) + 1
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")
    return items


# ============================================================
# Equipment Extraction (Mundane)
# ============================================================

def decode_html_entities(text: str) -> str:
    """Decode common HTML entities in item stat text."""
    return (text
            .replace('&ndash;', '-').replace('&mdash;', '—')
            .replace('&times;', 'x').replace('&amp;', '&')
            .replace('&lt;', '<').replace('&gt;', '>')
            .replace('\u2013', '-').replace('\u2014', '—')
            .replace('\u00d7', 'x'))


def normalize_field_name(field: str) -> str:
    """Normalize item_misc field names across books (UE has mangled names)."""
    f = field.strip().lower()
    f = re.sub(r'\s+', ' ', f)
    # Map known variants
    mapping = {
        'armorcheck penalty': 'armor check penalty',
        'armorbonus': 'armor bonus',
        'maximumdex bonus': 'maximum dex bonus',
        'maxdex bonus': 'maximum dex bonus',
        'arcane spellfailure': 'arcane spell failure chance',
        'arcane spellfailure chance': 'arcane spell failure chance',
        'shieldbonus': 'shield bonus',
    }
    return mapping.get(f, f)


def extract_equipment() -> list[Equipment]:
    """Extract mundane equipment (weapons, armor, gear) from PSRD data."""
    print("\n=== Extracting Equipment ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database
        FROM central_index
        WHERE type = 'item'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} total item entries in index")

    # Collect by name, preferring UE over other books
    items_by_name: dict[str, dict] = {}

    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']
        item_name = entry['name']
        source = entry['source']

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()

        # Check if item is mundane (no aura)
        dcur.execute("SELECT aura, price, weight FROM item_details WHERE section_id = ?",
                     (section_id,))
        details = dcur.fetchone()
        if not details:
            continue
        if details['aura'] and details['aura'].strip() and details['aura'].strip() != 'no aura (nonmagical)':
            continue  # Skip magic items

        price = details['price'] or ''
        weight = details['weight'] or ''

        # Get item_misc stats
        dcur.execute("SELECT field, value, subsection FROM item_misc WHERE section_id = ?",
                     (section_id,))
        misc_rows = dcur.fetchall()

        stats: dict[str, str] = {}
        for row in misc_rows:
            field_name = normalize_field_name(row['field'] or '')
            value = decode_html_entities(row['value'] or '')
            stats[field_name] = value

        # Build weapon stats
        weapon_stats = None
        weapon_fields = {'dmg (m)', 'dmg (s)', 'critical', 'type', 'proficiency', 'weapon class'}
        if any(f in stats for f in weapon_fields):
            weapon_stats = WeaponStats(
                damage_medium=stats.get('dmg (m)', ''),
                damage_small=stats.get('dmg (s)', ''),
                critical=stats.get('critical', ''),
                damage_type=stats.get('type', ''),
                range_increment=stats.get('range', ''),
                proficiency=stats.get('proficiency', ''),
                weapon_class=stats.get('weapon class', ''),
                special=stats.get('special', ''),
            )

        # Build armor stats
        armor_stats = None
        armor_fields = {'armor bonus', 'shield bonus', 'maximum dex bonus', 'armor check penalty'}
        if any(f in stats for f in armor_fields):
            ab = stats.get('armor bonus', '0')
            sb = stats.get('shield bonus', '0')
            mdb = stats.get('maximum dex bonus', '')
            acp = stats.get('armor check penalty', '0')
            asf = stats.get('arcane spell failure chance', '0')
            sp30 = stats.get('speed (30 ft.)', None)
            sp20 = stats.get('speed (20 ft.)', None)

            def parse_int(s: str, default: int = 0) -> int:
                s = s.strip().replace('+', '').replace('–', '-').replace('—', '-').rstrip('%')
                if not s or s == '-':
                    return default
                try:
                    return int(s)
                except ValueError:
                    return default

            armor_stats = ArmorStats(
                armor_bonus=parse_int(ab),
                shield_bonus=parse_int(sb),
                max_dex_bonus=parse_int(mdb) if mdb.strip() and mdb.strip() not in ('-', '—') else None,
                armor_check_penalty=parse_int(acp),
                arcane_spell_failure=parse_int(asf),
                speed_30=sp30,
                speed_20=sp20,
            )

        # Determine category
        if weapon_stats:
            category = 'weapon'
        elif armor_stats:
            if armor_stats.shield_bonus > 0:
                category = 'shield'
            else:
                category = 'armor'
        else:
            category = 'gear'

        # Get description
        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        body_row = dcur.fetchone()
        description = html_to_text(body_row['body']) if body_row and body_row['body'] else ''
        if len(description) > 500:
            description = description[:500] + '...'

        name_key = item_name.strip().lower()
        # Prefer UE over other books
        if name_key not in items_by_name or db_name == 'book-ue.db':
            items_by_name[name_key] = {
                'name': item_name,
                'source': source,
                'category': category,
                'price': price,
                'weight': weight,
                'description': description,
                'weapon_stats': weapon_stats,
                'armor_stats': armor_stats,
            }

    equipment = []
    for data in items_by_name.values():
        eq = Equipment(
            name=data['name'],
            source=data['source'],
            category=data['category'],
            price=data['price'],
            weight=data['weight'],
            description=data['description'],
            weapon_stats=data['weapon_stats'],
            armor_stats=data['armor_stats'],
        )
        equipment.append(eq)

    equipment.sort(key=lambda e: e.name)

    cat_counts: dict[str, int] = {}
    for e in equipment:
        cat_counts[e.category] = cat_counts.get(e.category, 0) + 1
    print(f"  Extracted {len(equipment)} mundane equipment items")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {cnt}")
    return equipment


# ============================================================
# Race Extraction
# ============================================================

def extract_races() -> list[Race]:
    """Extract all races from PSRD data."""
    print("\n=== Extracting Races ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database, subtype
        FROM central_index
        WHERE type = 'race'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} race entries in index")

    races = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']
        race_name = entry['name']
        source = entry['source']

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()

        # Get body description
        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        main = dcur.fetchone()
        description = html_to_text(main['body']) if main and main['body'] else ''
        if len(description) > 500:
            description = description[:500] + '...'

        # Get racial traits
        dcur.execute("SELECT lft, rgt FROM sections WHERE section_id = ?", (section_id,))
        bounds = dcur.fetchone()
        if not bounds:
            continue

        dcur.execute("""
            SELECT section_id, name, type, subtype, body
            FROM sections
            WHERE lft > ? AND rgt < ? AND type = 'racial_trait'
            ORDER BY lft
        """, (bounds['lft'], bounds['rgt']))
        trait_sections = dcur.fetchall()

        racial_traits: list[RacialTrait] = []
        ability_modifiers: list[dict] = []
        size = 'Medium'
        speed: list[dict] = []
        languages: dict = {'starting': [], 'bonus': []}
        race_type = 'humanoid'
        subtypes: list[str] = []

        for trait in trait_sections:
            trait_name = trait['name'] or ''
            trait_body = html_to_text(trait['body'])

            # Detect ability score modifiers from traits
            if trait_name.lower() in ('attributes', 'ability score modifiers', 'ability scores'):
                # Parse "+2 Dex, +2 Int, -2 Str" patterns
                mod_matches = re.findall(r'([+-]\d+)\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma|Str|Dex|Con|Int|Wis|Cha)', trait_body, re.IGNORECASE)
                ability_map = {
                    'strength': 'STR', 'str': 'STR',
                    'dexterity': 'DEX', 'dex': 'DEX',
                    'constitution': 'CON', 'con': 'CON',
                    'intelligence': 'INT', 'int': 'INT',
                    'wisdom': 'WIS', 'wis': 'WIS',
                    'charisma': 'CHA', 'cha': 'CHA',
                }
                for mod_str, ability in mod_matches:
                    ability_modifiers.append({
                        'ability': ability_map.get(ability.lower(), ability.upper()[:3]),
                        'modifier': int(mod_str)
                    })
                continue

            # Detect size
            if trait_name.lower() in ('small', 'medium', 'large', 'tiny'):
                size = trait_name.capitalize()
                continue

            # Detect speed
            if 'speed' in trait_name.lower():
                speed_match = re.search(r'(\d+)\s*(?:feet|ft)', trait_body)
                if speed_match:
                    speed.append({'type': 'land', 'value': int(speed_match.group(1))})
                continue

            # Detect type
            if 'type' in trait_name.lower() and trait_name.lower() not in ('weapon familiarity',):
                type_match = re.search(r'(humanoid|outsider|fey|dragon|monstrous humanoid|aberration|undead)', trait_body, re.IGNORECASE)
                if type_match:
                    race_type = type_match.group(1).lower()
                subtype_matches = re.findall(r'\(([^)]+)\)', trait_body)
                for st in subtype_matches:
                    subtypes.extend([s.strip() for s in st.split(',')])
                continue

            # Detect languages
            if 'language' in trait_name.lower():
                starting_match = re.search(r'begin play speaking\s+(.+?)\.', trait_body, re.IGNORECASE)
                if starting_match:
                    languages['starting'] = [l.strip() for l in starting_match.group(1).split(' and ')]
                    # Flatten "Common and Elven" type patterns
                    flat = []
                    for l in languages['starting']:
                        flat.extend([x.strip() for x in l.split(',')])
                    languages['starting'] = [l for l in flat if l]

                bonus_match = re.search(r'can choose from the following:\s*(.+?)(?:\.|$)', trait_body, re.IGNORECASE)
                if not bonus_match:
                    bonus_match = re.search(r'bonus languages?:\s*(.+?)(?:\.|$)', trait_body, re.IGNORECASE)
                if bonus_match:
                    languages['bonus'] = [l.strip() for l in bonus_match.group(1).split(',') if l.strip()]
                continue

            # Regular racial trait
            if len(trait_body) > 500:
                trait_body = trait_body[:500] + '...'

            racial_traits.append(RacialTrait(
                name=trait_name,
                description=trait_body,
            ))

        if not speed:
            speed = [{'type': 'land', 'value': 30}]

        race = Race(
            name=race_name,
            source=source,
            description=description,
            type=race_type,
            subtypes=subtypes,
            size=size,
            speed=speed,
            ability_modifiers=ability_modifiers,
            languages=languages,
            racial_traits=racial_traits,
        )
        races.append(race)
        print(f"  {race_name} ({source}) {size} {race_type} mods={ability_modifiers}")

    return races


# ============================================================
# Skill Extraction
# ============================================================

def extract_skills() -> list[Skill]:
    """Extract all skills from PSRD data."""
    print("\n=== Extracting Skills ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database,
               skill_attribute, skill_armor_check_penalty, skill_trained_only,
               description
        FROM central_index
        WHERE type = 'skill'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} skill entries in index")

    # Deduplicate by name (skills may appear in multiple books)
    seen: set[str] = set()
    skills = []
    for entry in entries:
        name = entry['name']
        if name in seen:
            continue
        seen.add(name)

        ability = (entry['skill_attribute'] or 'INT').upper()
        if ability in ('STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'):
            pass
        else:
            # Map full names
            ability_map = {'STRENGTH': 'STR', 'DEXTERITY': 'DEX', 'CONSTITUTION': 'CON',
                           'INTELLIGENCE': 'INT', 'WISDOM': 'WIS', 'CHARISMA': 'CHA'}
            ability = ability_map.get(ability.upper(), ability[:3].upper())

        skill = Skill(
            name=name,
            ability=ability,
            trained_only=bool(entry['skill_trained_only']),
            armor_check_penalty=bool(entry['skill_armor_check_penalty']),
            description=entry['description'] or '',
        )
        skills.append(skill)
        print(f"  {name} ({ability}) trained={skill.trained_only} acp={skill.armor_check_penalty}")

    return skills


# ============================================================
# Alternate Racial Traits Extraction
# ============================================================

def extract_alternate_racial_traits(races: list[Race]) -> None:
    """Populate alternate_racial_traits on existing Race objects from PSRD data."""
    print("\n=== Extracting Alternate Racial Traits ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database, subtype
        FROM central_index
        WHERE type = 'racial_trait'
        ORDER BY subtype, name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} racial trait entries in index")

    # Build race lookup by normalized name
    race_by_name: dict[str, Race] = {}
    for race in races:
        race_by_name[race.name.strip().lower()] = race

    # Normalize race subtype → race name mapping
    # The subtype field uses things like "dwarf", "elf", "half_orc", "dwarves", "elves"
    subtype_to_race: dict[str, str] = {}
    # Map singular subtype forms → plural race_by_name keys
    singular_to_plural = {
        'dwarf': 'dwarves', 'elf': 'elves', 'gnome': 'gnomes',
        'halfling': 'halflings', 'human': 'humans',
        'half-elf': 'half-elves', 'half-orc': 'half-orcs',
        'half_elf': 'half-elves', 'half_orc': 'half-orcs',
        'gillman': 'gillmen',
    }
    for race in races:
        name_lower = race.name.strip().lower()
        subtype_to_race[name_lower] = name_lower
        subtype_to_race[name_lower.replace('-', '_')] = name_lower
        subtype_to_race[name_lower.replace('-', ' ')] = name_lower
    for singular, plural in singular_to_plural.items():
        if plural in race_by_name:
            subtype_to_race[singular] = plural

    traits_added = 0
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']
        trait_name = entry['name']
        subtype = (entry['subtype'] or '').strip().lower()

        # Find the race this trait belongs to
        race_name = subtype_to_race.get(subtype)
        if not race_name or race_name not in race_by_name:
            continue

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()
        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        section = dcur.fetchone()
        if not section:
            continue

        body = html_to_text(section['body'])

        # Parse "replaces" from body
        replaces: list[str] = []
        replace_match = re.search(
            r'This (?:racial )?trait replaces (.+?)\.', body, re.IGNORECASE)
        if replace_match:
            replaces_text = replace_match.group(1)
            # Split on " and " then ","
            parts = re.split(r'\s+and\s+|,\s*', replaces_text)
            replaces = [p.strip() for p in parts if p.strip()]

        if len(body) > 500:
            body = body[:500] + '...'

        race_by_name[race_name].alternate_racial_traits.append(
            AlternateRacialTrait(
                name=trait_name,
                description=body,
                replaces=replaces,
            )
        )
        traits_added += 1

    races_with_alts = sum(1 for r in races if r.alternate_racial_traits)
    print(f"  Added {traits_added} alternate racial traits to {races_with_alts} races")


# ============================================================
# Domain / Bloodline / Mystery / Patron Extraction
# ============================================================

def parse_domain_spells(html_body: str) -> list[DomainSpellEntry]:
    """Parse spell list from domain/patron format: '1st—spell name, 2nd—spell name'."""
    text = html_to_text(html_body)
    entries = []
    # Match patterns like "1st—burning hands" or "2nd-produce flame"
    for m in re.finditer(r'(\d+)(?:st|nd|rd|th)?[—–\-]+\s*(.+?)(?:,\s*|\.\s*|$)', text):
        level = int(m.group(1))
        spell_name = m.group(2).strip().rstrip('.')
        if spell_name:
            entries.append(DomainSpellEntry(level=level, spell_name=spell_name))
    return entries


def parse_bloodline_spells(html_body: str) -> list[DomainSpellEntry]:
    """Parse spell list from bloodline/mystery format: 'spell name (3rd), spell name (5th)'."""
    text = html_to_text(html_body)
    entries = []
    # Match "spell name (3rd)" or "spell name (5th)"
    for m in re.finditer(r'([^,()]+?)\s*\((\d+)(?:st|nd|rd|th)\)', text):
        spell_name = m.group(1).strip().rstrip(',').strip()
        level = int(m.group(2))
        if spell_name:
            entries.append(DomainSpellEntry(level=level, spell_name=spell_name))
    return entries


def extract_domains() -> list[Domain]:
    """Extract cleric domains from PSRD data."""
    print("\n=== Extracting Domains ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database
        FROM central_index
        WHERE type = 'section' AND subtype = 'cleric_domain'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} domain entries")

    domains = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()

        # Get domain description
        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        main = dcur.fetchone()
        description = html_to_text(main['body']) if main and main['body'] else ''
        if len(description) > 500:
            description = description[:500] + '...'

        # Get children
        dcur.execute("""
            SELECT name, body FROM sections
            WHERE parent_id = ? ORDER BY lft
        """, (section_id,))
        children = dcur.fetchall()

        granted_powers = ''
        spells: list[DomainSpellEntry] = []
        for child in children:
            child_name = (child['name'] or '').strip()
            child_body = child['body'] or ''
            if 'granted power' in child_name.lower() or 'granted' in child_name.lower():
                granted_powers = html_to_text(child_body)
                if len(granted_powers) > 1000:
                    granted_powers = granted_powers[:1000] + '...'
            elif 'spell' in child_name.lower():
                spells = parse_domain_spells(child_body)

        domains.append(Domain(
            name=entry['name'],
            source=entry['source'],
            description=description,
            granted_powers=granted_powers,
            spells=spells,
        ))

    print(f"  Extracted {len(domains)} domains, "
          f"{sum(1 for d in domains if d.spells)} with spell lists")
    return domains


def extract_subdomains() -> list[Subdomain]:
    """Extract cleric subdomains from PSRD data."""
    print("\n=== Extracting Subdomains ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database, parent_name
        FROM central_index
        WHERE type = 'section' AND subtype = 'cleric_subdomain'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} subdomain entries")

    subdomains = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']
        parent_domain = entry['parent_name'] or ''

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()
        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        section = dcur.fetchone()
        body = html_to_text(section['body']) if section and section['body'] else ''

        # Parse replaced and replacement powers
        replaced = ''
        replacement = ''
        replaced_match = re.search(
            r'Replacement Power[s]?:\s*(.+?)(?:$)', body, re.IGNORECASE)
        if replaced_match:
            replacement = replaced_match.group(1).strip()

        if len(body) > 1000:
            body = body[:1000] + '...'

        subdomains.append(Subdomain(
            name=entry['name'],
            domain=parent_domain,
            source=entry['source'],
            description=body,
            replaced_powers=replaced,
            replacement_powers=replacement,
        ))

    print(f"  Extracted {len(subdomains)} subdomains")
    return subdomains


def extract_bloodlines() -> list[Bloodline]:
    """Extract sorcerer bloodlines from PSRD data."""
    print("\n=== Extracting Bloodlines ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database
        FROM central_index
        WHERE type = 'section' AND subtype = 'sorcerer_bloodline'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} bloodline entries")

    bloodlines = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()

        # Get description
        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        main = dcur.fetchone()
        description = html_to_text(main['body']) if main and main['body'] else ''
        if len(description) > 500:
            description = description[:500] + '...'

        # Get children
        dcur.execute("""
            SELECT name, body FROM sections
            WHERE parent_id = ? ORDER BY lft
        """, (section_id,))
        children = dcur.fetchall()

        class_skill = ''
        bonus_spells: list[DomainSpellEntry] = []
        bonus_feats = ''
        bloodline_arcana = ''
        bloodline_powers = ''

        for child in children:
            child_name = (child['name'] or '').strip().lower()
            child_body = child['body'] or ''
            child_text = html_to_text(child_body)

            if 'class skill' in child_name:
                class_skill = child_text
            elif 'bonus spell' in child_name:
                bonus_spells = parse_bloodline_spells(child_body)
            elif 'bonus feat' in child_name:
                bonus_feats = child_text
                if len(bonus_feats) > 500:
                    bonus_feats = bonus_feats[:500] + '...'
            elif 'arcana' in child_name:
                bloodline_arcana = child_text
                if len(bloodline_arcana) > 500:
                    bloodline_arcana = bloodline_arcana[:500] + '...'
            elif 'power' in child_name:
                bloodline_powers = child_text
                if len(bloodline_powers) > 1000:
                    bloodline_powers = bloodline_powers[:1000] + '...'

        bloodlines.append(Bloodline(
            name=entry['name'],
            source=entry['source'],
            description=description,
            class_skill=class_skill,
            bonus_spells=bonus_spells,
            bonus_feats=bonus_feats,
            bloodline_arcana=bloodline_arcana,
            bloodline_powers=bloodline_powers,
        ))

    print(f"  Extracted {len(bloodlines)} bloodlines, "
          f"{sum(1 for b in bloodlines if b.bonus_spells)} with spell lists")
    return bloodlines


def extract_oracle_mysteries() -> list[OracleMystery]:
    """Extract oracle mysteries from PSRD data."""
    print("\n=== Extracting Oracle Mysteries ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database
        FROM central_index
        WHERE type = 'section' AND subtype = 'oracle_mystery'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} oracle mystery entries")

    mysteries = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()

        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        main = dcur.fetchone()
        description = html_to_text(main['body']) if main and main['body'] else ''
        if len(description) > 500:
            description = description[:500] + '...'

        # Get children
        dcur.execute("""
            SELECT name, body FROM sections
            WHERE parent_id = ? ORDER BY lft
        """, (section_id,))
        children = dcur.fetchall()

        class_skills: list[str] = []
        bonus_spells: list[DomainSpellEntry] = []
        revelations = ''

        for child in children:
            child_name = (child['name'] or '').strip().lower()
            child_body = child['body'] or ''
            child_text = html_to_text(child_body)

            if 'class skill' in child_name:
                # Parse individual skills from text
                skills_raw = re.findall(r'([A-Z][\w\s]+?)(?:\s*\(|,|\.|\band\b)', child_text)
                class_skills = [s.strip() for s in skills_raw if s.strip()]
            elif 'bonus spell' in child_name or 'spell' in child_name:
                bonus_spells = parse_bloodline_spells(child_body)
            elif 'revelation' in child_name:
                revelations = child_text
                if len(revelations) > 1000:
                    revelations = revelations[:1000] + '...'

        mysteries.append(OracleMystery(
            name=entry['name'],
            source=entry['source'],
            description=description,
            class_skills=class_skills,
            bonus_spells=bonus_spells,
            revelations=revelations,
        ))

    print(f"  Extracted {len(mysteries)} oracle mysteries, "
          f"{sum(1 for m in mysteries if m.bonus_spells)} with spell lists")
    return mysteries


def extract_witch_patrons() -> list[WitchPatron]:
    """Extract witch patrons from PSRD data."""
    print("\n=== Extracting Witch Patrons ===")
    idx = get_index_db()
    cur = idx.cursor()

    cur.execute("""
        SELECT index_id, section_id, name, source, database
        FROM central_index
        WHERE type = 'section' AND subtype = 'witch_patron'
        ORDER BY name
    """)
    entries = cur.fetchall()
    print(f"  Found {len(entries)} witch patron entries")

    patrons = []
    for entry in entries:
        db_name = entry['database']
        section_id = entry['section_id']

        try:
            db = get_db(db_name)
        except FileNotFoundError:
            continue

        dcur = db.cursor()
        dcur.execute("SELECT body FROM sections WHERE section_id = ?", (section_id,))
        section = dcur.fetchone()
        if not section or not section['body']:
            continue

        # Patron spells are in the body directly, using domain format
        spells = parse_domain_spells(section['body'])

        patrons.append(WitchPatron(
            name=entry['name'],
            source=entry['source'],
            spells=spells,
        ))

    print(f"  Extracted {len(patrons)} witch patrons, "
          f"{sum(1 for p in patrons if p.spells)} with spell lists")
    return patrons


# ============================================================
# Prestige Class Requirements (integrated into extract_classes)
# ============================================================

def parse_prestige_requirements(all_descendants: list, section_id: int, db: sqlite3.Connection) -> list[PrestigeRequirement]:
    """Parse prestige class entry requirements from descendant sections."""
    dcur = db.cursor()

    # Find the "Requirements" section
    req_section_id = None
    req_body = None
    for desc in all_descendants:
        desc_name = (desc['name'] or '').strip().lower()
        if desc_name in ('requirements', 'requirement', 'entry requirements'):
            req_section_id = desc['section_id']
            req_body = desc['body'] or ''
            break

    if req_section_id is None:
        return []

    requirements: list[PrestigeRequirement] = []

    # Check for sub-sections under the requirements section
    children = [d for d in all_descendants if d['parent_id'] == req_section_id]

    if children:
        for child in children:
            child_name = (child['name'] or '').strip()
            child_body = html_to_text(child['body'] or '')
            name_lower = child_name.lower()

            if 'base attack' in name_lower or 'bab' in name_lower:
                m = re.search(r'\+(\d+)', child_body)
                requirements.append(PrestigeRequirement(
                    type='bab', text=child_body,
                    value=int(m.group(1)) if m else 0))
            elif 'feat' in name_lower:
                items = [f.strip().rstrip('.') for f in re.split(r',\s*', child_body) if f.strip()]
                requirements.append(PrestigeRequirement(
                    type='feats', text=child_body, items=items))
            elif 'skill' in name_lower:
                items = [s.strip().rstrip('.') for s in re.split(r',\s*(?=[A-Z])', child_body) if s.strip()]
                requirements.append(PrestigeRequirement(
                    type='skills', text=child_body, items=items))
            elif 'spell' in name_lower:
                m = re.search(r'(\d+)(?:st|nd|rd|th)', child_body)
                requirements.append(PrestigeRequirement(
                    type='spells', text=child_body,
                    value=int(m.group(1)) if m else 0))
            elif 'alignment' in name_lower:
                requirements.append(PrestigeRequirement(
                    type='alignment', text=child_body))
            else:
                requirements.append(PrestigeRequirement(
                    type='special', text=child_body))
    else:
        # Requirements in a single text block
        text = html_to_text(req_body)
        if not text:
            return []

        # Try to parse structured requirements from text
        bab_match = re.search(r'Base Attack Bonus[:\s]*\+(\d+)', text, re.IGNORECASE)
        if bab_match:
            requirements.append(PrestigeRequirement(
                type='bab', text=f'+{bab_match.group(1)}',
                value=int(bab_match.group(1))))

        feats_match = re.search(r'Feats?[:\s]*(.+?)(?:Skills?|Spells?|Special|Alignment|$)',
                                text, re.IGNORECASE | re.DOTALL)
        if feats_match:
            feats_text = feats_match.group(1).strip().rstrip('.')
            items = [f.strip().rstrip('.') for f in re.split(r',\s*', feats_text) if f.strip()]
            if items:
                requirements.append(PrestigeRequirement(
                    type='feats', text=feats_text, items=items))

        skills_match = re.search(r'Skills?[:\s]*(.+?)(?:Feats?|Spells?|Special|Alignment|$)',
                                 text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1).strip().rstrip('.')
            items = [s.strip().rstrip('.') for s in re.split(r',\s*(?=[A-Z])', skills_text) if s.strip()]
            if items:
                requirements.append(PrestigeRequirement(
                    type='skills', text=skills_text, items=items))

        spells_match = re.search(r'Spells?[:\s]*(.+?)(?:Feats?|Skills?|Special|Alignment|$)',
                                 text, re.IGNORECASE | re.DOTALL)
        if spells_match:
            spells_text = spells_match.group(1).strip().rstrip('.')
            m = re.search(r'(\d+)(?:st|nd|rd|th)', spells_text)
            requirements.append(PrestigeRequirement(
                type='spells', text=spells_text,
                value=int(m.group(1)) if m else 0))

        special_match = re.search(r'Special[:\s]*(.+?)(?:Feats?|Skills?|Spells?|Alignment|$)',
                                  text, re.IGNORECASE | re.DOTALL)
        if special_match:
            requirements.append(PrestigeRequirement(
                type='special', text=special_match.group(1).strip().rstrip('.')))

        alignment_match = re.search(r'Alignment[:\s]*(.+?)(?:Feats?|Skills?|Spells?|Special|$)',
                                    text, re.IGNORECASE | re.DOTALL)
        if alignment_match:
            requirements.append(PrestigeRequirement(
                type='alignment', text=alignment_match.group(1).strip().rstrip('.')))

    return requirements


# ============================================================
# Main
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("PSRD Data Extraction")
    print(f"  Source: {RAW_DIR}")
    print(f"  Output: {OUTPUT_DIR}")

    skills = extract_skills()
    save_json(skills, os.path.join(OUTPUT_DIR, 'skills.json'))

    races = extract_races()
    extract_alternate_racial_traits(races)
    save_json(races, os.path.join(OUTPUT_DIR, 'races.json'))

    classes = extract_classes()
    save_json(classes, os.path.join(OUTPUT_DIR, 'classes.json'))

    archetypes = extract_archetypes()
    save_json(archetypes, os.path.join(OUTPUT_DIR, 'archetypes.json'))

    spells = extract_spells()
    save_json(spells, os.path.join(OUTPUT_DIR, 'spells.json'))

    feats = extract_feats()
    save_json(feats, os.path.join(OUTPUT_DIR, 'feats.json'))

    items = extract_items()
    save_json(items, os.path.join(OUTPUT_DIR, 'items.json'))

    equipment = extract_equipment()
    save_json(equipment, os.path.join(OUTPUT_DIR, 'equipment.json'))

    # Class options (domains, bloodlines, mysteries, patrons)
    domains = extract_domains()
    subdomains = extract_subdomains()
    bloodlines = extract_bloodlines()
    oracle_mysteries = extract_oracle_mysteries()
    witch_patrons = extract_witch_patrons()

    class_options = {
        'domains': [asdict(d) for d in domains],
        'subdomains': [asdict(s) for s in subdomains],
        'bloodlines': [asdict(b) for b in bloodlines],
        'oracle_mysteries': [asdict(m) for m in oracle_mysteries],
        'witch_patrons': [asdict(p) for p in witch_patrons],
    }
    class_options_path = os.path.join(OUTPUT_DIR, 'class_options.json')
    with open(class_options_path, 'w', encoding='utf-8') as f:
        json.dump(class_options, f, indent=2, ensure_ascii=False)
    print(f"  Saved {class_options_path}")

    # Summary
    prestige_with_reqs = sum(1 for c in classes if c.requirements)
    feats_with_prereqs = sum(1 for f in feats if f.parsed_prerequisites)
    races_with_alts = sum(1 for r in races if r.alternate_racial_traits)

    print("\n=== SUMMARY ===")
    print(f"  Skills:          {len(skills)}")
    print(f"  Races:           {len(races)} ({races_with_alts} with alt traits)")
    print(f"  Classes:         {len(classes)} ({prestige_with_reqs} prestige with requirements)")
    print(f"  Archetypes:      {len(archetypes)}")
    print(f"  Spells:          {len(spells)}")
    print(f"  Feats:           {len(feats)} ({feats_with_prereqs} with parsed prereqs)")
    print(f"  Items:           {len(items)}")
    print(f"  Equipment:       {len(equipment)}")
    print(f"  Domains:         {len(domains)}")
    print(f"  Subdomains:      {len(subdomains)}")
    print(f"  Bloodlines:      {len(bloodlines)}")
    print(f"  Oracle Mysteries:{len(oracle_mysteries)}")
    print(f"  Witch Patrons:   {len(witch_patrons)}")

    # Cleanup DB connections
    for conn in _db_cache.values():
        conn.close()


if __name__ == '__main__':
    main()
