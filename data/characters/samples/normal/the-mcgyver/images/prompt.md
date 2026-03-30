# The McGyver — Portrait Prompt

## Prompt

Copy and paste this into your preferred image generator:

```
fantasy illustration, detailed, warm tones, upper body portrait, slight angle, confident posture

Human Wizard (Spell Sage) 10

Brown mullet, weathered tan, denim robe, utility belt bristling with components

Angus "McGyver" Mallory never fit in at the Acadamae. While the other apprentices polished their wands and debated the finer points of abjuration theory, Angus was in the back of the workshop disassembling a wand of magic missile to see how the crystallized evocation matrix interfaced with the wood grain.

After leaving formal education behind, Angus spent a decade on the road — caravan guard, dungeon delver, freelance problem-solver. He earned the name "McGyver" from a dwarven mining crew after he sealed a collapsed tunnel using nothing but a wall of stone (borrowed from the druid list, naturally), a bag of ball bearings, and a ten-foot pole.

You can spot McGyver from a hundred yards: the mullet is unmistakable, a glorious waterfall of brown hair cascading over the collar of his denim robe (he had it commissioned from a bemused tailor in Absalom — "like a wizard's robe, but tougher, with more pockets").

Practical and rugged feel, not pristine or regal. Workshop or dungeon background with arcane tools. Warm torchlight.

No text, watermarks, or UI elements in the image.
```

## Settings

- **Style**: fantasy illustration, detailed, warm tones
- **Framing**: upper body portrait, slight angle, confident posture
- **Recommended aspect ratio**: 2:3 (portrait) or 1:1 (token)
- **Recommended resolution**: 1024x1536 or 1024x1024

## How to generate and add to the character sheet

1. Copy the prompt above
2. Paste it into your preferred image generator:
   - [ChatGPT](https://chatgpt.com) — use "create an image" or the DALL-E tool
   - [Google Gemini](https://gemini.google.com) — ask it to generate an image
   - [Midjourney](https://www.midjourney.com) — paste in Discord with /imagine
   - [Stable Diffusion](https://stability.ai) — use locally or via DreamStudio
   - Any other text-to-image tool
3. Download the generated image(s)
4. Save them to this directory (`images/`) as `portrait.png` (or `portrait-1.png`, `portrait-2.png` for variants)
5. Reference in sheet.md by adding an Images section after the title:

```markdown
## Images

| | |
|---|---|
| ![Portrait](images/portrait.png) | ![Alt](images/portrait-2.png) |
```

## Regeneration

To generate a new prompt with different settings, use:
```
generate_portrait_prompt(character_dir="data/characters/samples/normal/the-mcgyver", style="...", framing="...", extra_directions="...")
```
