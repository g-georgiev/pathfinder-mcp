---
name: create-character
description: "Create a standardized Pathfinder character sheet from any input format. Accepts character data as chat, pasted text, JSON file, or rough description and generates a complete multi-file character directory."
user-invocable: true
argument-hint: "Character data or path to a file containing character data"
---

# Create Character Sheet

You are helping the user create a standardized Pathfinder 1e character sheet. You handle ALL data lookups (MCP tools), then spawn the character-builder agent to generate the files.

## Step 1: Gather Input

If the user provided character data in the arguments or conversation, use it. Otherwise, ask what they have:

- A Google Sheets export or pasted text?
- A JSON file from the data pipeline?
- A description they'll type out?
- An existing character file to convert?

Collect at minimum: **name, race, level, classes** (and archetypes if any), **ability scores**, **feats**, and **spells known**. Everything else can be derived or looked up, but flag what's missing.

## Step 2: Clarify Ambiguities

Before generating, resolve anything unclear:
- Is this a **gestalt** character? If two classes at the same level, assume yes.
- Any **archetypes**? Confirm compatibility if multiple on one class.
- Any **bloodline/mystery/domain** selections?
- Any **house rules** beyond what's in CLAUDE.md?
- Is there a **backstory** to include?

Keep this brief — don't interrogate. If the data is clear enough, move on.

## Step 3: Resolve All Game Data via MCP

**This is your main job.** The character-builder agent cannot access MCP tools, so you must pre-fetch everything it needs.

### 3a: Parse the character data

Extract lists of everything that needs lookup:
- All spell names (by class and level)
- All feat names
- Class name(s) and archetype name(s)
- Race name
- Class options (domains, bloodlines, mysteries, patrons)

### 3b: Batch MCP lookups

For each category, query the pathfinder-data MCP tools with `expand=True`:

- `search_spells(query=..., expand=True)` for each spell
- `search_feats(query=..., expand=True)` for each feat
- `search_classes(query=..., expand=True)` for each class
- `search_archetypes(query=..., base_class=..., expand=True)` for each archetype
- `search_races(query=..., expand=True)` for the race
- `search_class_options(query=..., option_type=..., expand=True)` for domains/bloodlines/etc.
- `check_feat_prerequisites(...)` for each feat against the character's stats
- `check_archetype_compatibility(...)` if multiple archetypes on one class

### 3c: Enrich stubs

For any result with `_stub: true`:
1. Web fetch the entry's `url` field
2. Extract the full description, school, class levels, prerequisites, etc.
3. Cache the enriched data via `cache_entry` (replaces the stub permanently)
4. Use the enriched version in the resolved data

### 3d: Handle missing entries

If a spell/feat/feature is not found in the DB at all:
1. Web search for it on aonprd.com or d20pfsrd.com
2. Extract and normalize the data
3. Cache it via `cache_entry` with ID prefixed `web-`
4. Include the result in the resolved data

### 3e: Write resolved data file

Write a JSON file at `/tmp/pf-character-{name}.json` with this structure:

```json
{
  "character": {
    "name": "...",
    "race": "...",
    "level": 13,
    "classes": [...],
    "alignment": "...",
    "deity": "...",
    "ability_scores": {...},
    "combat": {...},
    "skills": [...],
    "raw_input": "full text of original character data"
  },
  "resolved_data": {
    "spells": { "Fireball": { full expanded data... }, ... },
    "feats": { "Power Attack": { full expanded data... }, ... },
    "classes": { "Gunslinger": { full expanded data... }, ... },
    "archetypes": { "Musket Master": { full expanded data... }, ... },
    "race": { full expanded data... },
    "class_options": { "Luck": { full expanded data... }, ... }
  },
  "feat_prerequisites": {
    "Power Attack": { "qualified": true, "met": [...], "unmet": [...] },
    ...
  },
  "archetype_compatibility": { ... },
  "house_rules": "text of campaign house rules from personal CLAUDE.md",
  "output_dir": "/absolute/path/to/personal/characters/{name}/",
  "format_template": "/absolute/path/to/FORMAT.md"
}
```

## Step 4: Spawn the Agent

Spawn the `character-builder` agent:

```
Use the Agent tool with subagent_type="pathfinder:character-builder".

Prompt: "Generate a complete Pathfinder character sheet from the resolved data file at /tmp/pf-character-{name}.json. All game data (spells, feats, classes, features) has been pre-fetched — read it from the JSON file. Generate sheet.md, spells.md, features.md, and feats.md in the output directory specified in the file. Follow the FORMAT.md template exactly."
```

## Step 5: Review

After the agent completes, tell the user:
- Where the files are
- Any validation warnings or questions from the agent
- Offer to make corrections or adjustments

If the user provides images, create an `images/` subdirectory and wire them into the sheet header.
