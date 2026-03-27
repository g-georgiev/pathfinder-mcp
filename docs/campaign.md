# Campaign Context

Players may have campaign-specific data in their personal directory under `campaigns/{campaign_name}/`. This contains world-building notes, faction info, setting lore, and session context that the DM has shared or the player has compiled.

## When to Use Campaign Data

- The user asks about the world, setting, NPCs, factions, or locations
- The user asks "what do I know about X?" or "who is X?"
- Social encounters or diplomacy where faction relationships matter
- Lore questions about cosmology, history, or religions
- Planning actions that depend on setting context (e.g. "would Cheliax help us?")
- Roleplay or in-character moments that benefit from world knowledge

## How to Use It

1. Check if campaign data exists: look for `campaigns/` in the personal directory (sibling `personal/` to the plugin, or the current working directory)
2. Grep or read the relevant file based on the question
3. Combine campaign-specific lore with general Pathfinder knowledge from the DB
4. When campaign lore contradicts standard Golarion canon, the campaign version takes precedence — it's the DM's world

## Don't Over-Read

Campaign files can be large. Don't read everything upfront — grep for the relevant topic first, then read the specific section. Only read `world.md` or `inspiration.md` in full if the user is asking broad setting questions.

## File Conventions

Campaign data typically follows this structure (but players may organize differently):

| File | Content |
|------|---------|
| `world.md` | Cosmology, timeline, major setting rules |
| `factions.md` | Nations, organizations, key NPCs, political relationships |
| `{location}.md` | Specific location details (cities, dungeons, regions) |
| `inspiration.md` | Source material the campaign draws from (tone, themes, mechanics to expect) |
| `sessions.md` | Session logs or summaries (if maintained) |
| `npcs.md` | NPC relationships and attitudes toward the party |
