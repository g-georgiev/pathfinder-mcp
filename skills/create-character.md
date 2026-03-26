---
name: create-character
description: "Create a standardized Pathfinder character sheet from any input format. Accepts character data as chat, pasted text, JSON file, or rough description and generates a complete multi-file character directory."
user_invocable: true
arguments:
  - name: input
    description: "Character data or path to a file containing character data. Can be omitted to provide data interactively."
    required: false
---

# Create Character Sheet

You are helping the user create a standardized Pathfinder 1e character sheet.

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

## Step 3: Build

Spawn the `character-builder` agent to do the heavy lifting:

```
Use the Agent tool with subagent_type="pathfinder:character-builder" to generate the character sheet.
Pass it ALL the character data collected so far, including:
- The full character data (stats, feats, spells, etc.)
- The path to the personal data directory (../personal/ relative to the plugin)
- Any house rules from the personal CLAUDE.md
```

The agent will:
1. Parse the input
2. Look up all spells/feats/features in the DB (web search + cache if missing)
3. Generate `sheet.md`, `spells.md`, `features.md`, `feats.md`
4. Validate calculations
5. Report back with files created and any warnings

## Step 4: Review

After the agent completes, tell the user:
- Where the files are: `data/characters/{name}/`
- Any validation warnings or questions from the agent
- Offer to make corrections or adjustments

If the user provides images, create an `images/` subdirectory and wire them into the sheet header.
