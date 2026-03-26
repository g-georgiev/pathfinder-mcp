"""
Scrape aonprd.com for comprehensive Pathfinder 1e data.

Strategy:
  1. Spell index from Spells.aspx?Class=All (single request, all spells)
  2. Feat index by iterating all categories from Feats.aspx
  3. Archetype lists by iterating all classes from Classes.aspx
     (includes explicit "Replaces" column)
  4. Class list from Classes.aspx

Merges with existing PSRD data to fill gaps.
"""

import os
import sys
import re
import json
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(__file__))
from utils import RateLimitedFetcher, clean_text

AONPRD_BASE = "https://aonprd.com"
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'aonprd')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')

fetcher = RateLimitedFetcher(delay=1.0, cache_dir=CACHE_DIR)


# ============================================================
# HTML Parsers for aonprd page structures
# ============================================================

class LinkExtractor(HTMLParser):
    """Extract all <a> links from HTML content."""

    def __init__(self):
        super().__init__()
        self.links: list[dict] = []  # [{"href": ..., "text": ...}]
        self.current_href: str | None = None
        self.current_text = ''
        self.in_link = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            attrs_dict = dict(attrs)
            self.current_href = attrs_dict.get('href', '')
            self.current_text = ''
            self.in_link = True

    def handle_endtag(self, tag):
        if tag.lower() == 'a' and self.in_link:
            self.in_link = False
            if self.current_href:
                self.links.append({
                    'href': self.current_href,
                    'text': self.current_text.strip()
                })

    def handle_data(self, data):
        if self.in_link:
            self.current_text += data


class AonprdTableParser(HTMLParser):
    """Parse aonprd data tables (feats, archetypes, etc.)."""

    def __init__(self):
        super().__init__()
        self.rows: list[list[str]] = []
        self.headers: list[str] = []
        self.current_row: list[str] = []
        self.current_cell = ''
        self.in_cell = False
        self.in_thead = False
        self.in_header_row = False
        self.cell_links: list[dict] = []
        self.current_link_href = ''
        self.current_link_text = ''
        self.in_link = False
        self.row_links: list[list[dict]] = []
        self.current_row_links: list[dict] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)
        if tag == 'tr':
            self.current_row = []
            self.current_row_links = []
            # Detect header rows by style
            style = attrs_dict.get('style', '')
            if 'font-weight:bold' in style or 'font-weight: bold' in style:
                self.in_header_row = True
        elif tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = ''
            self.cell_links = []
        elif tag == 'a' and self.in_cell:
            self.in_link = True
            self.current_link_href = attrs_dict.get('href', '')
            self.current_link_text = ''
        elif tag == 'br' and self.in_cell:
            self.current_cell += '; '
        elif tag == 'img':
            pass  # skip PFS images

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ('td', 'th'):
            self.in_cell = False
            cell_text = self.current_cell.strip()
            self.current_row.append(cell_text)
            self.current_row_links.append(self.cell_links[0] if self.cell_links else {})
        elif tag == 'a' and self.in_link:
            self.in_link = False
            if self.current_link_href:
                self.cell_links.append({
                    'href': self.current_link_href,
                    'text': self.current_link_text.strip()
                })
            # Add link text to cell content
            self.current_cell += self.current_link_text
        elif tag == 'tr':
            if self.current_row:
                if self.in_header_row:
                    self.headers = self.current_row
                    self.in_header_row = False
                else:
                    self.rows.append(self.current_row)
                    self.row_links.append(self.current_row_links)

    def handle_data(self, data):
        if self.in_link:
            self.current_link_text += data
        elif self.in_cell:
            self.current_cell += data

    def handle_entityref(self, name):
        entities = {'mdash': '—', 'ndash': '–', 'amp': '&', 'lt': '<', 'gt': '>'}
        char = entities.get(name, f'&{name};')
        if self.in_link:
            self.current_link_text += char
        elif self.in_cell:
            self.current_cell += char


class SpellListParser(HTMLParser):
    """Parse aonprd Spells.aspx?Class=All page to extract spell names and URLs."""

    def __init__(self):
        super().__init__()
        self.spells: list[dict] = []  # [{"name": ..., "url": ..., "description": ...}]
        self.in_spell_span = False
        self.in_link = False
        self.current_href = ''
        self.current_name = ''
        self.current_text = ''
        self.span_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)
        span_id = attrs_dict.get('id', '')

        if tag == 'span' and 'DataListTypes_LabelName_' in span_id:
            self.in_spell_span = True
            self.current_text = ''
            self.span_depth = 1
        elif tag == 'span' and self.in_spell_span:
            self.span_depth += 1
        elif tag == 'a' and self.in_spell_span:
            href = attrs_dict.get('href', '')
            if 'SpellDisplay.aspx' in href:
                self.in_link = True
                self.current_href = href
                self.current_name = ''
        elif tag == 'br' and self.in_spell_span:
            self.current_text += '\n'

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'a' and self.in_link:
            self.in_link = False
        elif tag == 'span' and self.in_spell_span:
            self.span_depth -= 1
            if self.span_depth <= 0:
                self.in_spell_span = False
                # Extract description from accumulated text
                desc = self.current_text.strip()
                # Remove leading colon and whitespace
                desc = re.sub(r'^:\s*', '', desc).strip()
                # Get first line only
                desc = desc.split('\n')[0].strip()
                if self.current_href:
                    self.spells.append({
                        'name': self.current_name.strip(),
                        'url': self.current_href,
                        'description': desc,
                    })
                self.current_href = ''
                self.current_name = ''
                self.current_text = ''

    def handle_data(self, data):
        if self.in_link:
            self.current_name += data
        elif self.in_spell_span:
            self.current_text += data


# ============================================================
# Extract content from div#main
# ============================================================

class MainContentExtractor(HTMLParser):
    """Extract the content inside div#main from an aonprd page."""

    def __init__(self):
        super().__init__()
        self.in_main = False
        self.depth = 0
        self.content_parts: list[str] = []
        self.raw_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div' and attrs_dict.get('id') == 'main':
            self.in_main = True
            self.depth = 1
            return
        if self.in_main:
            if tag == 'div':
                self.depth += 1
            # Reconstruct the HTML
            attr_str = ' '.join(f'{k}="{v}"' for k, v in attrs)
            self.raw_parts.append(f'<{tag}{" " + attr_str if attr_str else ""}>')

    def handle_endtag(self, tag):
        if self.in_main:
            if tag == 'div':
                self.depth -= 1
                if self.depth <= 0:
                    self.in_main = False
                    return
            self.raw_parts.append(f'</{tag}>')

    def handle_data(self, data):
        if self.in_main:
            self.raw_parts.append(data)
            self.content_parts.append(data)

    def handle_entityref(self, name):
        if self.in_main:
            self.raw_parts.append(f'&{name};')

    def get_html(self) -> str:
        return ''.join(self.raw_parts)

    def get_text(self) -> str:
        return ''.join(self.content_parts)


def extract_main_content(html: str) -> str:
    """Extract the innerHTML of div#main from a full page."""
    ext = MainContentExtractor()
    ext.feed(html)
    return ext.get_html()


# ============================================================
# Scraping Functions
# ============================================================

def scrape_class_list() -> list[dict]:
    """Get list of all classes from Classes.aspx."""
    print("  Fetching class list...")
    html = fetcher.fetch(f"{AONPRD_BASE}/Classes.aspx")
    parser = LinkExtractor()
    parser.feed(html)

    classes = []
    for link in parser.links:
        if 'ClassDisplay.aspx?ItemName=' in link['href']:
            name = link['text'].strip()
            if name and name not in ('', 'Prestige Classes'):
                classes.append({
                    'name': name,
                    'url': link['href'],
                })

    # Deduplicate
    seen = set()
    unique = []
    for c in classes:
        if c['name'] not in seen:
            seen.add(c['name'])
            unique.append(c)

    print(f"  Found {len(unique)} classes")
    return unique


def scrape_spell_index() -> list[dict]:
    """Scrape complete spell index from Spells.aspx?Class=All."""
    print("  Fetching spell index (all spells, single request)...")
    html = fetcher.fetch(f"{AONPRD_BASE}/Spells.aspx?Class=All")

    parser = SpellListParser()
    parser.feed(html)

    print(f"  Found {len(parser.spells)} spells")
    return parser.spells


def scrape_feat_categories() -> list[str]:
    """Get list of feat categories from Feats.aspx."""
    html = fetcher.fetch(f"{AONPRD_BASE}/Feats.aspx")
    parser = LinkExtractor()
    parser.feed(html)

    categories = []
    for link in parser.links:
        href = link['href']
        if 'Feats.aspx?Category=' in href:
            cat_match = re.search(r'Category=([^&]*)', href)
            if cat_match:
                cat = cat_match.group(1)
                categories.append(cat)

    # Deduplicate, include empty string (General category)
    seen = set()
    unique = []
    for c in categories:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    return unique


def scrape_feat_index() -> list[dict]:
    """Scrape feat index from all category pages."""
    print("  Fetching feat categories...")
    categories = scrape_feat_categories()
    print(f"  Found {len(categories)} feat categories")

    all_feats: dict[str, dict] = {}  # keyed by name to deduplicate

    for cat in categories:
        cat_label = cat if cat else 'General'
        url = f"{AONPRD_BASE}/Feats.aspx?Category={cat}"
        html = fetcher.fetch(url)

        parser = AonprdTableParser()
        parser.feed(html)

        count = 0
        for i, row in enumerate(parser.rows):
            if len(row) < 3:
                continue
            name = row[0].strip()
            # Clean name (remove PFS Legal text)
            name = re.sub(r'PFS Legal\s*', '', name).strip()
            if not name:
                continue

            link = parser.row_links[i][0] if i < len(parser.row_links) and parser.row_links[i] else {}
            href = link.get('href', '')
            feat_url = href if 'FeatDisplay.aspx' in href else None

            if name not in all_feats:
                all_feats[name] = {
                    'name': name,
                    'prerequisites': row[1].strip() if len(row) > 1 else '',
                    'description': row[2].strip() if len(row) > 2 else '',
                    'category': cat_label,
                    'url': feat_url,
                }
                count += 1

        print(f"    {cat_label}: {count} new feats ({len(parser.rows)} total in category)")

    feats = list(all_feats.values())
    print(f"  Total unique feats: {len(feats)}")
    return feats


def scrape_archetype_index() -> list[dict]:
    """Scrape archetype lists for all classes."""
    print("  Fetching class list for archetype scraping...")
    classes = scrape_class_list()

    all_archetypes: list[dict] = []

    for cls in classes:
        class_name = cls['name']
        url = f"{AONPRD_BASE}/Archetypes.aspx?Class={class_name.replace(' ', '+')}"

        try:
            html = fetcher.fetch(url)
        except Exception as e:
            print(f"    SKIP {class_name}: {e}")
            continue

        parser = AonprdTableParser()
        parser.feed(html)

        if not parser.rows:
            continue

        count = 0
        for i, row in enumerate(parser.rows):
            if len(row) < 2:
                continue
            name = row[0].strip()
            name = re.sub(r'PFS Legal\s*', '', name).strip()
            if not name:
                continue

            link = parser.row_links[i][0] if i < len(parser.row_links) and parser.row_links[i] else {}
            href = link.get('href', '')

            replaces_text = row[1].strip() if len(row) > 1 else ''
            summary = row[2].strip() if len(row) > 2 else ''

            all_archetypes.append({
                'name': name,
                'base_class': class_name,
                'replaces': replaces_text,
                'summary': summary,
                'url': href if 'ArchetypeDisplay.aspx' in href else None,
            })
            count += 1

        if count > 0:
            print(f"    {class_name}: {count} archetypes")

    print(f"  Total archetypes: {len(all_archetypes)}")
    return all_archetypes


# ============================================================
# Main
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    print("aonprd.com Scraping")
    print(f"  Cache: {CACHE_DIR}")
    print(f"  Output: {OUTPUT_DIR}")

    # 1. Spell index
    print("\n=== Scraping Spell Index ===")
    spell_index = scrape_spell_index()
    with open(os.path.join(OUTPUT_DIR, 'aonprd_spells.json'), 'w') as f:
        json.dump(spell_index, f, indent=2, ensure_ascii=False)
    print(f"  Saved aonprd_spells.json ({len(spell_index)} spells)")

    # 2. Feat index
    print("\n=== Scraping Feat Index ===")
    feat_index = scrape_feat_index()
    with open(os.path.join(OUTPUT_DIR, 'aonprd_feats.json'), 'w') as f:
        json.dump(feat_index, f, indent=2, ensure_ascii=False)
    print(f"  Saved aonprd_feats.json ({len(feat_index)} feats)")

    # 3. Archetype index
    print("\n=== Scraping Archetype Index ===")
    archetype_index = scrape_archetype_index()
    with open(os.path.join(OUTPUT_DIR, 'aonprd_archetypes.json'), 'w') as f:
        json.dump(archetype_index, f, indent=2, ensure_ascii=False)
    print(f"  Saved aonprd_archetypes.json ({len(archetype_index)} archetypes)")

    # Summary
    print("\n=== AONPRD SCRAPE SUMMARY ===")
    print(f"  Spells:     {len(spell_index)}")
    print(f"  Feats:      {len(feat_index)}")
    print(f"  Archetypes: {len(archetype_index)}")


if __name__ == '__main__':
    main()
