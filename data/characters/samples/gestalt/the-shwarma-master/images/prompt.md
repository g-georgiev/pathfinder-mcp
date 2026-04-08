# The Shwarma Master — Portrait Prompt

## Prompt

Copy and paste this into your preferred image generator:

```
fantasy illustration, detailed, warm Mediterranean tones, painterly, upper body portrait, slight three-quarter angle, calm meditative pose

Human Magus (Kensai) 16 / Wizard (Foresight Divination) 16 (gestalt)

Lean but hard-muscled from two decades at the spit. Dark olive skin, thick black hair on every surface it can grow — forearms, chest, back, knuckles. A single uninterrupted brow sits above watchful dark eyes. The mustache is enormous, oiled, and sculpted with meticulous pride — arguably his second-finest work, after the shwarma. He wears loose trousers and a stained apron tied with arcane sigils, both of which have survived grease fires, demon ichor, and worse sauces. [Aisha](#attacks), his scimitar, hangs at the hip; she smells faintly of cumin and ozone.

It involves a shipment of rare saffron from Osirion that never arrived. It involves a rival chef — or possibly a false chef, a demon wearing the face of a chef — who has been copying his recipes without his permission and selling them in the markets of Sothis under a name that is almost, but not quite, his own.

So he has packed his spice belt. He has tied *Aisha* at his hip. He has rolled his cooking stones into his travel pack. He has locked the door of the stand on the Avenue of Small Quarrels and pinned a note to it that reads, in elegant Kelish, *"Closed for investigation. Will return. Do not touch the jars."*

Burly-lean Qadiran human man with dark olive skin, thick jet-black hair on every visible surface (forearms, chest, back of hands), a single heavy unibrow, dark watchful eyes, an enormous oiled sculpted mustache (the character's second-finest work after the shwarma itself). He wears loose trousers and a heavily stained apron tied with arcane Kelish sigils — the apron is scarred with oil burns, spice stains in twenty colors, and faint scorch marks shaped like runes. A curved scimitar named Aisha hangs at his hip, the blade inscribed in flowing Kelish script, smelling faintly of cumin and ozone. In one hand he holds the scimitar mid-shave against a rotating vertical shwarma spit behind him; thin curls of perfectly sliced meat falling through the air. His other hand is open, palm up, with faint blue-white electric arcs crackling between his fingers — Shocking Grasp mid-cast. Steam rises from the spit. Spice jars, a clay oven, and a hanging bundle of herbs visible in the background. His expression is serene, focused, meditative — not angry, not smiling, just completely present in his craft. Warm golden hour lighting from a market stall lantern. Nethys's half-light/half-dark sigil faintly visible on the apron's chest. Do not show full body. No text, watermarks, or UI.

No text, watermarks, or UI elements in the image.
```

## Settings

- **Style**: fantasy illustration, detailed, warm Mediterranean tones, painterly
- **Framing**: upper body portrait, slight three-quarter angle, calm meditative pose
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
generate_portrait_prompt(character_dir="data/characters/samples/gestalt/the-shwarma-master", style="...", framing="...", extra_directions="...")
```
