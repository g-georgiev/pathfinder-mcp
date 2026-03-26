#!/usr/bin/env python3
"""Split single-file guides into sections based on their TOC/heading structure."""

import os
import re
import json

# Maps guide directory -> list of (section_heading_pattern, filename, title)
# Patterns match the start of a line in the guide text.
GUIDE_SECTIONS = {
    "sorcerer-iluzry": [
        ("Introduction", "overview", "Introduction & Rating System"),
        ("Class Overview", "class-overview", "Class Overview & Chassis"),
        ("Roles and Ability Scores", "roles", "Roles and Ability Scores"),
        ("Races", "races", "Races"),
        ("Bloodlines and Heritages", "bloodlines", "Bloodlines and Heritages"),
        ("Spells and Spellcasting", "spells", "Spells and Spellcasting"),
        ("Archetypes", "archetypes", "Archetypes"),
        ("Multiclassing", "multiclass", "Multiclassing, VMC, and Prestige"),
        ("Feats", "feats", "Feats"),
        ("Equipment", "equipment", "Equipment"),
        ("Sample Builds", "builds", "Sample Builds"),
    ],
    "cleric-iluzry": [
        ("Introduction", "overview", "Introduction & Rating System"),
        ("Class Overview", "class-overview", "Class Overview & Chassis"),
        ("Gods and Worship", "gods", "Gods and Worship"),
        ("Roles", "roles", "Roles"),
        ("Ability Scores", "ability-scores", "Ability Scores"),
        ("Races", "races", "Races"),
        ("Domains & Subdomains", "domains", "Domains & Subdomains"),
    ],
    "cleric-oracle-warpriest-spells": [
        ("Introduction", "overview", "Introduction"),
        ("0th Level Spells", "level-0", "Orisons (0th Level)"),
        ("1st Level Spells", "level-1", "1st Level Spells"),
        ("2nd Level Spells", "level-2", "2nd Level Spells"),
        ("3rd Level Spells", "level-3", "3rd Level Spells"),
        ("4th Level Spells", "level-4", "4th Level Spells"),
        ("5th Level Spells", "level-5", "5th Level Spells"),
        ("6rd Level Spells", "level-6", "6th Level Spells"),
        ("7th Level Spells", "level-7", "7th Level Spells"),
        ("8th Level Spells", "level-8", "8th Level Spells"),
        ("9th Level Spells", "level-9", "9th Level Spells"),
    ],
    "fighter-marshmallow": [
        ("The Fighter (Class Overview)", "overview", "Class Overview"),
        ("Attributes", "attributes", "Attributes"),
        ("Non-Combat Roles", "roles", "Roles"),
        ("Skills", "skills", "Skills"),
        ("Races", "races", "Races"),
        ("Advanced Weapon Training", "weapon-training", "Advanced Weapon Training"),
        ("Advanced Armor Training", "armor-training", "Advanced Armor Training"),
        ("Feats", "feats", "Feats"),
        ("Combat Specialization by Role", "combat-roles", "Combat Specialization by Role"),
        ("Archetypes", "archetypes", "Archetypes"),
        ("Prestige Classes", "prestige", "Prestige Classes"),
        ("Equipment", "equipment", "Equipment"),
        ("Multiclassing", "multiclass", "Multiclassing"),
        ("Sample Builds", "builds", "Sample Builds"),
    ],
    "wondrous-items-guide": [
        ("Introduction", "overview", "Introduction & Tags"),
        ("Belts", "belts", "Belts"),
        ("Body", "body", "Body"),
        ("Chest", "chest", "Chest"),
        ("Eyes", "eyes", "Eyes"),
        ("Feet", "feet", "Feet"),
        ("Hands", "hands", "Hands"),
        ("Head", "head", "Head"),
        ("Headband", "headband", "Headband"),
        ("Neck", "neck", "Neck"),
        ("Shoulders", "shoulders", "Shoulders"),
        ("Wrists", "wrists", "Wrists"),
        ("Slotless", "slotless", "Slotless"),
    ],
    "gestalt-guide": [
        ("Contributions to the Guide", "overview", "Overview & Rating System"),
        ("=Alchemist", "alchemist", "Alchemist Combinations"),
        ("=Arcanist", "arcanist", "Arcanist Combinations"),
        ("=Barbarian", "barbarian", "Barbarian Combinations"),
        ("=Bard", "bard", "Bard Combinations"),
        ("=Bloodrager", "bloodrager", "Bloodrager Combinations"),
        ("=Brawler", "brawler", "Brawler Combinations"),
        ("=Cavalier", "cavalier", "Cavalier Combinations"),
        ("=Cleric", "cleric", "Cleric Combinations"),
        ("=Druid", "druid", "Druid Combinations"),
        ("=Fighter", "fighter", "Fighter Combinations"),
        ("=Gunslinger", "gunslinger", "Gunslinger Combinations"),
        ("=Hunter", "hunter", "Hunter Combinations"),
        ("=Inquisitor", "inquisitor", "Inquisitor Combinations"),
        ("=Investigator", "investigator", "Investigator Combinations"),
        ("=Kineticist", "kineticist", "Kineticist Combinations"),
        ("=Magus", "magus", "Magus Combinations"),
        ("=Medium", "medium", "Medium Combinations"),
        ("=Mesmerist", "mesmerist", "Mesmerist Combinations"),
        ("=Monk", "monk", "Monk Combinations"),
        ("=Occultist", "occultist", "Occultist Combinations"),
        ("=Oracle", "oracle", "Oracle Combinations"),
        ("=Paladin", "paladin", "Paladin Combinations"),
        ("=Psychic", "psychic", "Psychic Combinations"),
        ("=Ranger", "ranger", "Ranger Combinations"),
        ("=Rogue", "rogue", "Rogue Combinations"),
        ("=Shaman", "shaman", "Shaman Combinations"),
        ("=Skald", "skald", "Skald Combinations"),
        ("=Slayer", "slayer", "Slayer Combinations"),
        ("=Sorcerer", "sorcerer", "Sorcerer Combinations"),
        ("=Spiritualist", "spiritualist", "Spiritualist Combinations"),
        ("=Summoner", "summoner", "Summoner Combinations"),
        ("=Swashbuckler", "swashbuckler", "Swashbuckler Combinations"),
        ("=Vigilante", "vigilante", "Vigilante Combinations"),
        ("=Warpriest", "warpriest", "Warpriest Combinations"),
        ("=Witch", "witch", "Witch Combinations"),
        ("=Wizard", "wizard", "Wizard Combinations"),
    ],
    "prestige-classes-guide": [
        ("Rating System", "overview", "Rating System"),
        ("Core Prestige Classes", "core", "Core Prestige Classes"),
        ("Advanced Prestige Classes", "advanced", "Advanced Prestige Classes"),
        ("Obedience Classes", "obedience", "Obedience Prestige Classes"),
    ],
    "gunslinger-njolly": [
        ("Table of Content", "overview", "Overview & Rating System"),
        ("Abilities", "abilities", "Abilities & Races"),
        ("Traits", "traits", "Traits"),
        ("Class Features", "class-features", "Class Features"),
        ("Archetypes", "archetypes", "Archetypes"),
        ("Feats", "feats", "Feats"),
        ("Equipment", "equipment", "Equipment"),
        ("Sample Builds", "builds", "Sample Builds"),
    ],
    "traits-guide": [
        ("Part 1", "basics", "The Basics"),
        ("Combat Traits", "combat", "Combat Traits"),
        ("Faith Traits", "faith", "Faith Traits"),
        ("Magic Traits", "magic", "Magic Traits"),
        ("Social Traits", "social", "Social Traits"),
        ("Campaign Traits", "campaign", "Campaign Traits"),
        ("Racial Traits", "racial", "Racial Traits"),
        ("Regional Traits", "regional", "Regional Traits"),
        ("Religion Traits", "religion", "Religion Traits"),
        ("Equipment Traits", "equipment", "Equipment Traits"),
    ],
    "sorcerer-spells-iluzry": [
        ("Introduction", "overview", "Introduction & Rules"),
        ("Cantrips", "cantrips", "Cantrips"),
        ("1st Level", "level-1", "1st Level Spells"),
        ("2nd Level", "level-2", "2nd Level Spells"),
        ("3rd Level", "level-3", "3rd Level Spells"),
        ("4th Level", "level-4", "4th Level Spells"),
        ("5th Level", "level-5", "5th Level Spells"),
        ("6th Level", "level-6", "6th Level Spells"),
        ("7th Level", "level-7", "7th Level Spells"),
        ("8th Level", "level-8", "8th Level Spells"),
        ("9th Level", "level-9", "9th Level Spells"),
    ],
    "alchemist-iluzry": [
        ("Introduction", "overview", "Introduction & Rating System"),
        ("Class Overview", "class-overview", "Class Overview & Chassis"),
        ("Roles", "roles", "Roles & Ability Scores"),
        ("Races", "races", "Races"),
        ("Discoveries", "discoveries", "Discoveries"),
        ("Extracts", "extracts", "Extracts & Alchemical Casting"),
        ("Archetypes", "archetypes", "Archetypes"),
        ("Multiclassing", "multiclass", "Multiclassing & Prestige"),
        ("Feats", "feats", "Feats"),
        ("Equipment", "equipment", "Equipment"),
        ("Sample Builds", "builds", "Sample Builds"),
    ],
    "paladin-iluzry": [
        ("Introduction", "overview", "Introduction & Rating System"),
        ("Class Overview", "class-overview", "Class Overview & Chassis"),
        ("Roles and Ability Scores", "roles", "Roles and Ability Scores"),
        ("Races", "races", "Races"),
        ("Mercies", "mercies", "Mercies & Cruelties"),
        ("Animal Companions", "companions", "Animal Companions"),
        ("Paladin Spellcasting", "spells", "Spellcasting"),
        ("Archetypes", "archetypes", "Archetypes"),
        ("Multiclassing", "multiclass", "Multiclassing & Prestige"),
        ("Feats", "feats", "Feats"),
        ("Equipment", "equipment", "Equipment"),
        ("Sample Builds", "builds", "Sample Builds"),
    ],
    "bard-iluzry": [
        ("Introduction", "overview", "Introduction & Rating System"),
        ("Class Overview", "class-overview", "Class Overview & Chassis"),
        ("Roles and Ability Scores", "roles", "Roles and Ability Scores"),
        ("Races", "races", "Races"),
        ("Bardic Performances", "performances", "Bardic Performances"),
        ("Bardic Masterpieces", "masterpieces", "Bardic Masterpieces"),
        ("Spells", "spells", "Spells & Spellcasting"),
        ("Archetypes", "archetypes", "Archetypes"),
        ("Multiclassing", "multiclass", "Multiclassing & Prestige"),
        ("Feats", "feats", "Feats"),
        ("Equipment", "equipment", "Equipment"),
        ("Sample Builds", "builds", "Sample Builds"),
    ],
    "druid-iluzry": [
        ("Introduction", "overview", "Introduction & Rating System"),
        ("Class Overview", "class-overview", "Class Overview & Chassis"),
        ("Roles and Ability Scores", "roles", "Roles and Ability Scores"),
        ("Races", "races", "Races"),
        ("Wild Shape", "wildshape", "Wild Shape"),
        ("Druid Domains", "domains", "Domains"),
        ("Animal Companions", "companions", "Animal Companions"),
        ("Archetypes", "archetypes", "Archetypes"),
        ("Multiclassing", "multiclass", "Multiclassing & Prestige"),
        ("Feats", "feats", "Feats"),
        ("Equipment", "equipment", "Equipment"),
        ("Sample Builds", "builds", "Sample Builds"),
    ],
    "druid-spells-iluzry": [
        ("Introduction", "overview", "Introduction & Rules"),
        ("Cantrips", "cantrips", "Cantrips"),
        ("1st Level", "level-1", "1st Level Spells"),
        ("2nd Level", "level-2", "2nd Level Spells"),
        ("3rd Level", "level-3", "3rd Level Spells"),
        ("4th Level", "level-4", "4th Level Spells"),
        ("5th Level", "level-5", "5th Level Spells"),
        ("6th Level", "level-6", "6th Level Spells"),
        ("7th Level", "level-7", "7th Level Spells"),
        ("8th Level", "level-8", "8th Level Spells"),
        ("9th Level", "level-9", "9th Level Spells"),
    ],
}


def read_guide(dirname):
    path = f"data/guides/{dirname}/guide.md"
    if not os.path.exists(path):
        return None, None
    with open(path) as f:
        text = f.read()

    # Separate frontmatter
    frontmatter = ""
    body = text
    if text.startswith("---"):
        end = text.index("---", 3) + 3
        frontmatter = text[:end]
        body = text[end:].lstrip("\n")

    return frontmatter, body


def find_section_boundaries(body, sections):
    """Find line numbers where each section starts.

    Takes the LAST occurrence of each heading pattern to skip past
    the Table of Contents entries that appear near the top.
    """
    lines = body.split("\n")
    boundaries = []

    for pattern, filename, title in sections:
        exact = pattern.startswith("=")
        if exact:
            pattern = pattern[1:]

        last_match = None
        for i, line in enumerate(lines):
            s = line.strip()
            if exact:
                if s == pattern:
                    last_match = i
            else:
                if s.startswith(pattern):
                    last_match = i
        if last_match is None:
            # Try case-insensitive
            for i, line in enumerate(lines):
                s = line.strip()
                if exact:
                    if s.lower() == pattern.lower():
                        last_match = i
                else:
                    if s.lower().startswith(pattern.lower()):
                        last_match = i
        if last_match is not None:
            boundaries.append((last_match, filename, title))
        else:
            print(f"    WARNING: section '{pattern}' not found")

    # Sort by line number
    boundaries.sort(key=lambda x: x[0])
    return boundaries, lines


def split_guide(dirname):
    sections = GUIDE_SECTIONS[dirname]
    frontmatter, body = read_guide(dirname)

    if frontmatter is None:
        print(f"  SKIP {dirname}: already split (no guide.md)")
        return None

    # Parse frontmatter for index
    fm_lines = frontmatter.split("\n")
    fm_data = {}
    for line in fm_lines:
        if ":" in line and not line.startswith("---"):
            key, _, val = line.partition(":")
            fm_data[key.strip()] = val.strip()

    boundaries, lines = find_section_boundaries(body, sections)

    if not boundaries:
        print(f"  SKIP {dirname}: no sections found")
        return

    out_dir = f"data/guides/{dirname}"
    files_written = []

    for idx, (start_line, filename, title) in enumerate(boundaries):
        # Section goes from this boundary to the next
        if idx + 1 < len(boundaries):
            end_line = boundaries[idx + 1][0]
        else:
            end_line = len(lines)

        section_text = "\n".join(lines[start_line:end_line]).strip()

        filepath = os.path.join(out_dir, f"{filename}.md")
        with open(filepath, "w") as f:
            f.write(f"# {title}\n\n")
            f.write(section_text)
            f.write("\n")

        files_written.append((filename, title, len(section_text)))

    # Write index.md
    with open(os.path.join(out_dir, "index.md"), "w") as f:
        f.write(frontmatter + "\n\n")
        f.write(f"## Sections\n\n")
        f.write("| File | Section | Size |\n")
        f.write("|------|---------|------|\n")
        for fn, title, size in files_written:
            f.write(f"| [{fn}.md]({fn}.md) | {title} | {size // 1000}K |\n")

    # Remove the old single guide.md
    old_path = os.path.join(out_dir, "guide.md")
    if os.path.exists(old_path):
        os.remove(old_path)

    return files_written


if __name__ == "__main__":
    for dirname in GUIDE_SECTIONS:
        print(f"\n=== {dirname} ===")
        files = split_guide(dirname)
        if files:
            for fn, title, size in files:
                print(f"  {fn}.md — {size:,} chars")
            print(f"  Total: {len(files)} files")
