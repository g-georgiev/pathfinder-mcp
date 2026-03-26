"""
Shared utilities for scraping and parsing.
"""

import time
import re
import os
import json
import requests
from html.parser import HTMLParser
from typing import Optional


# === Rate-limited HTTP ===

class RateLimitedFetcher:
    """Fetcher with configurable delay between requests."""

    def __init__(self, delay: float = 1.0, cache_dir: Optional[str] = None):
        self.delay = delay
        self.cache_dir = cache_dir
        self.last_request_time = 0.0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PathfinderCharacterSheetApp/1.0 (personal project; data ETL)'
        })

    def _cache_path(self, url: str) -> Optional[str]:
        if not self.cache_dir:
            return None
        safe_name = re.sub(r'[^\w\-.]', '_', url.split('://', 1)[-1])[:200]
        return os.path.join(self.cache_dir, safe_name + '.html')

    def fetch(self, url: str, force_refresh: bool = False) -> str:
        # Check cache first
        cache_path = self._cache_path(url)
        if cache_path and os.path.exists(cache_path) and not force_refresh:
            with open(cache_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()

        # Rate limit
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        self.last_request_time = time.time()

        html = response.text

        # Cache if configured
        if cache_path:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return html


# === HTML Parsing Utilities ===

class TableParser(HTMLParser):
    """Parse HTML tables into list of rows (list of cell strings)."""

    def __init__(self):
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self.current_table: list[list[str]] = []
        self.current_row: list[str] = []
        self.current_cell: str = ''
        self.in_cell = False
        self.in_table = False
        self.skip_depth = 0  # For nested tables

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == 'table':
            if self.in_table:
                self.skip_depth += 1
            else:
                self.in_table = True
                self.current_table = []
        elif self.skip_depth > 0:
            return
        elif tag == 'tr':
            self.current_row = []
        elif tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = ''
        elif tag == 'br' and self.in_cell:
            self.current_cell += '\n'
        elif tag == 'sup' and self.in_cell:
            pass  # skip superscript markers

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'table':
            if self.skip_depth > 0:
                self.skip_depth -= 1
            else:
                if self.current_table:
                    self.tables.append(self.current_table)
                self.current_table = []
                self.in_table = False
        elif self.skip_depth > 0:
            return
        elif tag in ('td', 'th'):
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
        elif tag == 'tr':
            if self.current_row:
                self.current_table.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell and self.skip_depth == 0:
            self.current_cell += data


class TextExtractor(HTMLParser):
    """Extract plain text from HTML, stripping all tags."""

    def __init__(self):
        super().__init__()
        self.pieces: list[str] = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ('script', 'style'):
            self.skip = True
        elif tag.lower() == 'br':
            self.pieces.append('\n')
        elif tag.lower() in ('p', 'div', 'li'):
            self.pieces.append('\n')

    def handle_endtag(self, tag):
        if tag.lower() in ('script', 'style'):
            self.skip = False
        elif tag.lower() in ('p', 'div'):
            self.pieces.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.pieces.append(data)

    def get_text(self) -> str:
        return re.sub(r'\n{3,}', '\n\n', ''.join(self.pieces)).strip()


class SectionParser(HTMLParser):
    """
    Parse aonprd-style pages that use headers and paragraphs to define sections.
    Extracts sections as {title: str, content: str} pairs.
    """

    def __init__(self):
        super().__init__()
        self.sections: list[dict] = []
        self.current_title: Optional[str] = None
        self.current_content: list[str] = []
        self.in_header = False
        self.in_content = True
        self.current_tag = ''
        self.tag_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self.tag_stack.append(tag)
        if tag in ('h1', 'h2', 'h3', 'h4'):
            # Save previous section
            if self.current_title is not None:
                self.sections.append({
                    'title': self.current_title.strip(),
                    'content': ''.join(self.current_content).strip()
                })
            self.current_title = ''
            self.current_content = []
            self.in_header = True
        elif tag == 'br':
            self.current_content.append('\n')
        elif tag in ('p', 'div'):
            self.current_content.append('\n')
        self.current_tag = tag

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.tag_stack:
            self.tag_stack.pop()
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self.in_header = False

    def handle_data(self, data):
        if self.in_header:
            self.current_title = (self.current_title or '') + data
        else:
            self.current_content.append(data)

    def finalize(self) -> list[dict]:
        if self.current_title is not None:
            self.sections.append({
                'title': self.current_title.strip(),
                'content': ''.join(self.current_content).strip()
            })
        return self.sections


def parse_tables(html: str) -> list[list[list[str]]]:
    """Parse all HTML tables into lists of rows."""
    parser = TableParser()
    parser.feed(html)
    return parser.tables


def extract_text(html: str) -> str:
    """Strip HTML tags and return plain text."""
    extractor = TextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def clean_text(text: str) -> str:
    """Clean up whitespace in extracted text."""
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def download_file(url: str, dest: str):
    """Download a file with progress indication."""
    print(f"  Downloading {url}...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    total = int(response.headers.get('content-length', 0))
    downloaded = 0
    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded * 100 // total
                print(f"\r  {pct}% ({downloaded}/{total} bytes)", end='', flush=True)
    print(f"\r  Done: {dest} ({downloaded} bytes)")
