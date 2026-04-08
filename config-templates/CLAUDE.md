# Pathfinder 1e Advisor

This project uses the pathfinder-data MCP server for Pathfinder 1st Edition game data, optimization guides, and character management.

## Quick Start

When answering Pathfinder questions, use the MCP tools:
- `search_spells`, `search_feats`, `search_classes`, etc. for game data lookups
- `search_guides` for optimization advice from community guides
- `get_reference('advisor')` for advisor behavior guidelines (combat math, Discord dice syntax, state tracking)
- `get_reference('format')` for character sheet format specification
- `get_reference('campaign')` for campaign data conventions
- `get_guide_index()` for the full guide listing

## Campaign House Rules

Add your campaign's house rules here. Example:
- **CMB** uses DEX instead of STR
- **CMD** uses double DEX instead of DEX + STR
