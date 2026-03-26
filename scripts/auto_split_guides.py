#!/usr/bin/env python3
"""Auto-split large single-file guides by detecting TOC patterns."""

import os
import re
import json
import glob


def slugify(text):
    """Convert a heading to a filename-safe slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s)
    return s[:50].strip('-')


def find_toc_entries(lines):
    """Find table of contents entries near the top of the document."""
    toc = []
    in_toc = False
    blank_count = 0

    for i, line in enumerate(lines[:300]):
        s = line.strip()
        if 'table of contents' in s.lower() or s.lower() == 'contents':
            in_toc = True
            continue
        if in_toc:
            if not s:
                blank_count += 1
                if blank_count > 3 and len(toc) > 3:
                    break
                continue
            blank_count = 0
            if len(s) < 100 and not s.startswith('(') and not s.startswith('http'):
                toc.append(s)

    return toc


def match_toc_to_body(toc_entries, lines, min_section_size=500):
    """Match TOC entries to their actual positions in the body text.

    Uses last-occurrence matching to skip past the TOC itself.
    Only keeps sections that produce meaningful content (> min_section_size chars).
    """
    boundaries = []

    for entry in toc_entries:
        last_match = None
        for i, line in enumerate(lines):
            if line.strip() == entry:
                last_match = i
            elif line.strip().startswith(entry) and len(line.strip()) < len(entry) + 10:
                last_match = i

        if last_match is not None:
            slug = slugify(entry)
            if slug and slug not in [b[1] for b in boundaries]:
                boundaries.append((last_match, slug, entry))

    boundaries.sort(key=lambda x: x[0])

    # Filter out sections that are too small (likely TOC noise)
    filtered = []
    for idx, (start, slug, title) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            end = boundaries[idx + 1][0]
        else:
            end = len(lines)
        content_size = sum(len(l) for l in lines[start:end])
        if content_size >= min_section_size:
            filtered.append((start, slug, title))

    return filtered


def split_guide(dirname):
    guide_path = f"data/guides/{dirname}/guide.md"
    if not os.path.exists(guide_path):
        return None

    with open(guide_path) as f:
        text = f.read()

    # Separate frontmatter
    frontmatter = ""
    body = text
    if text.startswith("---"):
        end = text.index("---", 3) + 3
        frontmatter = text[:end]
        body = text[end:].lstrip("\n")

    lines = body.split("\n")

    # Find TOC
    toc_entries = find_toc_entries(lines)
    if len(toc_entries) < 3:
        return None  # Not enough TOC to split

    # Match to body
    boundaries = match_toc_to_body(toc_entries, lines)
    if len(boundaries) < 3:
        return None  # Not enough matched sections

    # Write section files
    out_dir = f"data/guides/{dirname}"
    files_written = []

    for idx, (start, slug, title) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            end = boundaries[idx + 1][0]
        else:
            end = len(lines)

        content = "\n".join(lines[start:end]).strip()
        filepath = os.path.join(out_dir, f"{slug}.md")
        with open(filepath, "w") as f:
            f.write(f"# {title}\n\n")
            f.write(content)
            f.write("\n")
        files_written.append((slug, title, len(content)))

    # Write index
    with open(os.path.join(out_dir, "index.md"), "w") as f:
        f.write(frontmatter + "\n\n")
        f.write("## Sections\n\n")
        f.write("| File | Section | Size |\n")
        f.write("|------|---------|------|\n")
        for fn, title, size in files_written:
            f.write(f"| [{fn}.md]({fn}.md) | {title} | {size // 1000}K |\n")

    # Remove old guide.md
    os.remove(guide_path)

    return files_written


if __name__ == "__main__":
    MIN_SIZE = 100_000  # Only split guides over 100K

    for guide_path in sorted(glob.glob("data/guides/*/guide.md")):
        size = os.path.getsize(guide_path)
        if size < MIN_SIZE:
            continue

        dirname = os.path.basename(os.path.dirname(guide_path))
        print(f"\n=== {dirname} ({size // 1000}K) ===")

        files = split_guide(dirname)
        if files:
            for fn, title, sz in files:
                print(f"  {fn}.md — {sz:,} chars")
            print(f"  Split into {len(files)} files")
        else:
            print(f"  SKIP: no usable TOC found")
