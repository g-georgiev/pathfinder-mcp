# Lady Lara Croft — Portrait Prompt

## Prompt

Copy and paste this into your preferred image generator:

```
fantasy illustration, detailed, cinematic lighting, cool desaturated tones with warm accent light, upper body portrait, slight three-quarter angle, confident stance

Human Gunslinger (Pistolero) 16 / Bard (Archaeologist) 16 (gestalt)

Tall, wiry, athletic — the body of someone who climbs for a living. Long dark hair tied in a single severe braid that falls past her shoulder blades. Sun-darkened skin from years of Osirian expeditions. Sharp grey eyes that miss nothing. She wears practical adventuring leathers — fitted dark trousers, a sleeveless blouse, bracers, climbing harness, sturdy boots, ammunition bandoleer. Two pistols holstered at her hips, carried low and tied to the thigh for fast draw. Speaks with a crisp, precise Chelaxian accent. Unsmiling when working. Exactly as charming as she needs to be, no more.

Her parents' estate passed to her in trust, managed by a family solicitor in Egorian. Her childhood, after the disappearance, was supervised by governesses and tutors and a succession of Chelaxian noble aunts who regarded her as a project.

She returned to Nex once, accompanied by three Pathfinder Society associates and a hired Garundi guide. Two of the Society associates died in the ruin. The third retired from adventuring permanently and now runs a bookshop in Magnimar where he does not discuss Lara Croft under any circumstances. The guide refused payment and walked into the desert alone.

Her gear is methodical. Her pistols are well-maintained and carried low on the thigh for fast draw. Her climbing equipment is inspected weekly. Her cartridge belt carries 200 rounds of powder-and-ball, distributed in three types: standard, incendiary, and a specially-commissioned salt-and-silver load for undead.

Tall athletic woman with a wiry climber's build — lean muscle, no bulk. Long dark hair in a single tight braid falling past her shoulder blades. Sun-darkened olive skin from years of desert expeditions. Sharp grey eyes, intelligent and watchful, with a hint of aristocratic severity. She wears fitted dark adventuring leathers — sleeveless fitted top showing toned arms, practical bracers on forearms, a leather climbing harness visible at her waist. An ammunition bandolier crosses her chest diagonally. Two flintlock pistols holstered low on her thighs, tied down for fast draw — the holsters are well-worn leather. No armor visible except the faint glint of a mithral chain shirt beneath her top. One hand rests casually on the grip of a holstered pistol, the other holds an ancient stone tablet she's examining with focused attention. Background: the interior of an ancient ruin — crumbling stone columns, hieroglyphs on the walls, dust motes in a shaft of golden light from above. Faint blue magical glow from glyphs on the walls. She is calm, composed, professional — not posing, not smiling, working. The look of someone who has done this a thousand times and will do it a thousand more. Chelaxian noble bearing visible in her posture even in field clothes. No text, watermarks, or UI elements in the image.

No text, watermarks, or UI elements in the image.
```

## Settings

- **Style**: fantasy illustration, detailed, cinematic lighting, cool desaturated tones with warm accent light
- **Framing**: upper body portrait, slight three-quarter angle, confident stance
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
generate_portrait_prompt(character_dir="data/characters/samples/gestalt/lady-croft", style="...", framing="...", extra_directions="...")
```
