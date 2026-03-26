#!/usr/bin/env python3
"""Extract docx guides into sectioned markdown files."""

import zipfile
import glob
import os
import json
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

GUIDES = [
    {
        "pattern": "*Inquisitor*",
        "dir": "data/guides/inquisitor-allerseelen",
        "title": "The Inquisitor\u2019s Symposium: A Guide to the Pathfinder Inquisitor",
        "author": "Allerseelen",
        "source": "https://docs.google.com/document/d/1sFi5J6RODbKOYJglbELAM7bSLq9XCo7DO9QEtywZC5k/edit",
        "topics": ["inquisitor", "domains", "inquisitions", "teamwork feats", "divine casting", "build guide"],
        "classes": ["inquisitor"],
        "sections": {
            "INQ101": ("overview", "Overview \u2014 Welcome to the Inquisition"),
            "INQ102": ("comparison", "Survey of Divine Classes"),
            "INQ109": ("leveling", "Inquisitorial Development"),
            "INQ165": ("combat-intro", "Intro to Combat Styles"),
            "INQ265": ("combat-advanced", "Advanced Combat Styles"),
            "INQ301": ("races", "Race and Inquisition"),
            "INQ351": ("domains", "Domain Analytics"),
            "INQ405": ("spells", "Spellcasting Survey"),
            "INQ440": ("feats", "Feat Dynamics"),
            "INQ495": ("equipment", "The Inquisitor\u2019s Arsenal"),
            "INQ621": ("archetypes", "Archetypal Inquisition"),
            "INQ705": ("multiclass", "Dips, VMC, Prestige, Gestalt"),
            "INQ750": ("builds", "Sample Builds"),
        },
    },
    {
        "pattern": "*Investigator*",
        "dir": "data/guides/investigator-allerseelen",
        "title": "The Investigator\u2019s Academy: A Guide to the Pathfinder Investigator",
        "author": "Allerseelen",
        "source": "https://docs.google.com/document/d/1BkI5ph1ZDPRt8YrkCl9hG1VF8vHYbkC1nMRT9RcQGGE/edit",
        "topics": ["investigator", "talents", "extracts", "alchemy", "build guide"],
        "classes": ["investigator"],
        "sections": {
            "INV 101": ("chassis", "Class Chassis"),
            "INV 102": ("comparison", "Comparative Investigation"),
            "INV 151": ("paths", "Investigator Paths"),
            "INV 201": ("races", "Races"),
            "INV 202": ("traits", "Traits"),
            "INV 240": ("extracts", "Extracts"),
            "INV 280": ("talents", "Talents"),
            "INV 305": ("feats", "Feats"),
            "INV 410": ("archetypes", "Archetypes"),
            "INV 605": ("multiclass", "Dips, Gestalt, and Prestige"),
            "INV 660": ("equipment", "Magic Items"),
            "INV 801": ("builds", "Sample Builds"),
        },
    },
    {
        "pattern": "*Arcane Trickster*",
        "dir": "data/guides/arcane-trickster-significantotter",
        "title": "Significantotter\u2019s Guide to the Arcane Trickster",
        "author": "Significantotter",
        "source": "https://docs.google.com/document/d/1tpOQy_vA7SiaeU-YV5NnHJwVHpy-L9Spt-9RNYu-gSg/edit",
        "topics": ["arcane trickster", "prestige class", "sneak attack", "rogue", "wizard", "build guide"],
        "classes": ["arcane trickster", "rogue", "wizard"],
        "sections": {
            "Introduction": ("overview", "Introduction"),
            "The Arcane": ("chassis", "The Arcane Trickster\u2019s Chassis"),
            "Prerequisites": ("prerequisites", "Prerequisites and Entry Classes"),
            "Races": ("races", "Races"),
            "Feats": ("feats", "Feats & Traits"),
            "Skills": ("skills", "Skills"),
            "Equipment": ("equipment", "Equipment"),
            "Wizard": ("spells", "Wizard/Sorcerer Spells for the Arcane Trickster"),
            "Alchemical": ("reagents", "Alchemical Reagents"),
            "The Thought": ("thought-thief", "The Thought Thief"),
            "Sample": ("builds", "Sample Builds"),
        },
    },
]


def extract_guide(docx_path, config):
    out_dir = config["dir"]
    os.makedirs(out_dir, exist_ok=True)

    z = zipfile.ZipFile(docx_path)
    doc = z.read("word/document.xml")
    tree = ET.fromstring(doc)
    paragraphs = tree.findall(".//w:p", NS)

    structured = []
    for p in paragraphs:
        pPr = p.find("w:pPr", NS)
        style = ""
        if pPr is not None:
            pStyle = pPr.find("w:pStyle", NS)
            if pStyle is not None:
                style = pStyle.get(f'{{{NS["w"]}}}val', "")
        texts = p.findall(".//w:t", NS)
        line = "".join(t.text or "" for t in texts).strip()
        if line:
            structured.append((style, line))

    # Split into H1 sections
    sections = {}
    current_key = None
    current_lines = []

    for style, line in structured:
        if "Heading1" in style:
            if current_key:
                sections[current_key] = current_lines
            current_key = None
            for code in config["sections"]:
                if line.startswith(code):
                    current_key = code
                    break
            if current_key is None:
                current_key = f"_skip_{line[:20]}"
            current_lines = []
        else:
            md_line = line
            if "Heading2" in style:
                md_line = f"## {line}"
            elif "Heading3" in style:
                md_line = f"### {line}"
            elif "Heading4" in style:
                md_line = f"#### {line}"
            current_lines.append(md_line)

    if current_key:
        sections[current_key] = current_lines

    # Write section files
    files_written = []
    for code, (filename, title) in config["sections"].items():
        if code not in sections:
            continue
        content = "\n\n".join(sections[code])
        filepath = os.path.join(out_dir, f"{filename}.md")
        with open(filepath, "w") as f:
            f.write(f"# {title}\n\n")
            f.write(content)
            f.write("\n")
        files_written.append((filename, title, len(content)))

    # Write index
    with open(os.path.join(out_dir, "index.md"), "w") as f:
        f.write(f"---\n")
        f.write(f'title: "{config["title"]}"\n')
        f.write(f'author: {config["author"]}\n')
        f.write(f'source: {config["source"]}\n')
        f.write(f'topics: {json.dumps(config["topics"])}\n')
        f.write(f'classes: {json.dumps(config["classes"])}\n')
        f.write(f'license: "Guide content by {config["author"]}, redistributed with attribution for non-commercial use."\n')
        f.write(f"---\n\n")
        f.write(f'# {config["title"]}\n\n')
        f.write(f'**Author**: {config["author"]}\n\n')
        f.write(f"## Sections\n\n")
        f.write(f"| File | Section | Size |\n")
        f.write(f"|------|---------|------|\n")
        for fn, title, size in files_written:
            f.write(f"| [{fn}.md]({fn}.md) | {title} | {size // 1000}K |\n")

    return files_written


if __name__ == "__main__":
    for config in GUIDES:
        matches = glob.glob(f"data/{config['pattern']}.docx")
        if not matches:
            print(f"NOT FOUND: {config['pattern']}")
            continue
        docx_path = matches[0]
        print(f"\n=== {config['title'][:60]} ===")
        print(f"  Source: {docx_path}")
        files = extract_guide(docx_path, config)
        for fn, title, size in files:
            print(f"  {fn}.md \u2014 {size:,} chars")
        print(f"  Total: {len(files)} files")
