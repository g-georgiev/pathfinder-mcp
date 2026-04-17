"""Character rendering tools — markdown export and import."""

import json
import re

from game_state import get_game_db
from tools.character import persist_character


def render_character_md(session_id: str, character_id: str) -> str:
    """Render a character's full sheet as FORMAT.md-spec markdown.

    Reads the character from the database and produces a markdown string
    with frontmatter, identity, ability scores, combat stats, skills,
    feats, and equipment sections.

    Args:
        session_id: The session the character belongs to
        character_id: The character's unique identifier

    Returns:
        Markdown string, or {"error": "..."} dict on failure.
    """
    db = get_game_db()
    try:
        row = db.execute(
            "SELECT * FROM characters WHERE id = ? AND session_id = ?",
            (character_id, session_id),
        ).fetchone()
        if not row:
            return {"error": f"Character '{character_id}' not found"}

        data = json.loads(row["data"] or "{}")
        computed = json.loads(row["computed"] or "{}")

        name = data.get("name", row["name"])
        race = data.get("race", row["race"])
        classes = data.get("classes", [])
        abilities = data.get("abilities", {})
        feats = data.get("feats", [])
        traits = data.get("traits", [])
        skills_ranks = data.get("skills", {})
        equipment = data.get("equipment", [])
        alignment = data.get("alignment", "")
        deity = data.get("deity", "")

        total_level = sum(c.get("level", 1) for c in classes)
        classes_str = " / ".join(
            f"{c.get('name', '?')} {c.get('level', 1)}" for c in classes
        )

        ability_mods = computed.get("ability_mods", {})
        hp_data = computed.get("hp", {})
        saves = computed.get("saves", {})
        bab = computed.get("bab", 0)
        ac = computed.get("ac", {})
        cmb_cmd = computed.get("cmb_cmd", {})
        initiative = computed.get("initiative", {})
        attacks = computed.get("attacks", [])
        skill_totals = computed.get("skills", {})
        spell_slots = computed.get("spell_slots", {})

        lines = []

        # --- Frontmatter ---
        lines.append("---")
        lines.append(f"name: {name}")
        lines.append(f"level: {total_level}")
        lines.append(f"classes: {classes_str}")
        lines.append(f"race: {race}")
        if alignment:
            lines.append(f'alignment: "{alignment}"')
        if deity:
            lines.append(f"deity: {deity}")
        lines.append("---")
        lines.append("")

        # --- Title & Identity ---
        lines.append(f"# {name}")
        lines.append(f"**Level {total_level} {race} {classes_str}**")
        lines.append("")

        # --- Ability Scores ---
        lines.append("## Ability Scores")
        lines.append("")
        lines.append("| Ability | Score | Mod |")
        lines.append("|---------|-------|-----|")
        for ab in ("str", "dex", "con", "int", "wis", "cha"):
            score = abilities.get(ab, 10)
            mod = ability_mods.get(ab, 0)
            mod_str = f"+{mod}" if mod >= 0 else str(mod)
            lines.append(f"| {ab.upper()} | {score} | {mod_str} |")
        lines.append("")

        # --- Combat Stats ---
        lines.append("## Combat Stats")
        lines.append("")

        # AC
        ac_components = ac.get("components", {})
        lines.append("### Armor Class")
        lines.append("")
        lines.append(f"**AC {ac.get('total', 10)}** | Touch {ac.get('touch', 10)} | Flat-footed {ac.get('flat_footed', 10)}")
        lines.append("")
        if ac_components:
            parts = []
            for comp, val in ac_components.items():
                if val != 0 or comp == "base":
                    parts.append(f"{comp}: {val}")
            lines.append(f"({', '.join(parts)})")
            lines.append("")

        # HP
        hp_breakdown = hp_data.get("breakdown", {})
        lines.append("### Hit Points")
        lines.append("")
        lines.append(f"**HP {hp_data.get('max', 0)}** | Current: {row['current_hp']}")
        lines.append("")
        if hp_breakdown:
            parts = []
            for comp, val in hp_breakdown.items():
                if val != 0:
                    parts.append(f"{comp}: {val}")
            if parts:
                lines.append(f"({', '.join(parts)})")
                lines.append("")

        # Saves
        lines.append("### Saving Throws")
        lines.append("")
        lines.append("| Save | Total |")
        lines.append("|------|-------|")
        for save_name in ("fort", "ref", "will"):
            val = saves.get(save_name, 0)
            val_str = f"+{val}" if val >= 0 else str(val)
            lines.append(f"| {save_name.capitalize()} | {val_str} |")
        lines.append("")

        # Offense
        lines.append("### Offense")
        lines.append("")
        lines.append(f"**BAB** +{bab}")
        init_total = initiative.get("total", 0)
        init_str = f"+{init_total}" if init_total >= 0 else str(init_total)
        lines.append(f"**Initiative** {init_str}")
        lines.append(f"**CMB** +{cmb_cmd.get('cmb', 0)} | **CMD** {cmb_cmd.get('cmd', 10)}")
        lines.append("")

        # Attacks
        if attacks:
            lines.append("### Attacks")
            lines.append("")
            lines.append("| Weapon | Attack | Damage | Crit |")
            lines.append("|--------|--------|--------|------|")
            for atk in attacks:
                ab_list = atk.get("ab", [])
                ab_str = "/".join(
                    f"+{a}" if a >= 0 else str(a) for a in ab_list
                )
                lines.append(
                    f"| {atk.get('name', '?')} | {ab_str} | {atk.get('damage', '?')} | {atk.get('crit', '?')} |"
                )
            lines.append("")
            # Notes
            for atk in attacks:
                for note in atk.get("notes", []):
                    lines.append(f"*{note}*")
            if any(atk.get("notes") for atk in attacks):
                lines.append("")

        # --- Skills ---
        if skill_totals:
            lines.append("## Skills")
            lines.append("")
            lines.append("| Skill | Total | Ranks |")
            lines.append("|-------|-------|-------|")
            for skill_name in sorted(skill_totals.keys()):
                total = skill_totals[skill_name]
                ranks = skills_ranks.get(skill_name, 0)
                total_str = f"+{total}" if total >= 0 else str(total)
                lines.append(f"| {skill_name.capitalize()} | {total_str} | {ranks} |")
            lines.append("")

        # --- Feats ---
        if feats:
            lines.append("## Feats")
            lines.append("")
            lines.append("| Level | Feat | Notes |")
            lines.append("|-------|------|-------|")
            for feat in feats:
                level = feat.get("level_taken", "?")
                fname = feat.get("name", "?")
                notes = feat.get("notes", feat.get("effect", ""))
                lines.append(f"| {level} | {fname} | {notes} |")
            lines.append("")

        # --- Traits ---
        if traits:
            lines.append("## Traits")
            lines.append("")
            lines.append("| Trait | Effect |")
            lines.append("|-------|--------|")
            for trait in traits:
                tname = trait.get("name", "?")
                effect = trait.get("effect", "")
                lines.append(f"| {tname} | {effect} |")
            lines.append("")

        # --- Equipment ---
        if equipment:
            lines.append("## Equipment")
            lines.append("")
            for item in equipment:
                item_name = item.get("name", "?")
                slot = item.get("slot", "")
                lines.append(f"- **{item_name}**" + (f" ({slot})" if slot else ""))
            lines.append("")

        gold = data.get("gold", 0)
        if gold:
            lines.append(f"**Gold**: {gold} gp")
            lines.append("")

        # --- Spellcasting ---
        if spell_slots:
            lines.append("## Spellcasting")
            lines.append("")
            for cls_name, slots in spell_slots.items():
                lines.append(f"### {cls_name.capitalize()} Spells")
                lines.append("")
                lines.append("| Level | Slots |")
                lines.append("|-------|-------|")
                for level_str in sorted(slots.keys(), key=lambda x: int(x)):
                    lines.append(f"| {level_str} | {slots[level_str]} |")
                lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def import_character_md(
    session_id: str,
    player_id: str,
    md_text: str,
) -> dict:
    """Parse a markdown character sheet and persist it.

    Extracts frontmatter (YAML between ---), ability score table, feat
    list, equipment, skills, and traits from the markdown text. Best-effort
    parsing: unparseable sections are flagged as warnings.

    Args:
        session_id: The session to import into
        player_id: The player who owns this character
        md_text: The markdown text to parse

    Returns:
        dict with character_id and warnings list.
    """
    warnings = []
    character_data = {}

    try:
        # --- Parse frontmatter ---
        fm_match = re.search(r"^---\s*\n(.*?)\n---", md_text, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            for line in fm_text.strip().split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip().strip('"').strip("'")

                    if key == "name":
                        character_data["name"] = value
                    elif key == "race":
                        character_data["race"] = value
                    elif key == "alignment":
                        character_data["alignment"] = value
                    elif key == "deity":
                        character_data["deity"] = value
                    elif key == "level":
                        pass  # Computed from classes
                    elif key == "classes":
                        # Parse "Fighter 5" or "Fighter 5 / Rogue 3"
                        classes = []
                        parts = [p.strip() for p in value.split("/")]
                        for part in parts:
                            # Handle gestalt notation
                            part = part.replace("(gestalt)", "").strip()
                            tokens = part.rsplit(None, 1)
                            if len(tokens) == 2 and tokens[1].isdigit():
                                classes.append({
                                    "name": tokens[0],
                                    "level": int(tokens[1]),
                                })
                            else:
                                classes.append({"name": part, "level": 1})
                                warnings.append(f"Could not parse level from class: '{part}'")
                        character_data["classes"] = classes
        else:
            warnings.append("No frontmatter found (expected --- delimiters)")

        # --- Parse Ability Scores table ---
        ab_pattern = re.compile(
            r"\|\s*(STR|DEX|CON|INT|WIS|CHA)\s*\|\s*(\d+)\s*\|",
            re.IGNORECASE,
        )
        abilities = {}
        for match in ab_pattern.finditer(md_text):
            ab_name = match.group(1).lower()
            ab_score = int(match.group(2))
            abilities[ab_name] = ab_score
        if abilities:
            character_data["abilities"] = abilities
        else:
            warnings.append("Could not parse ability scores table")

        # --- Parse Feats table ---
        feats = []
        feat_pattern = re.compile(
            r"\|\s*(\d+|\?)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|"
        )
        in_feats_section = False
        for line in md_text.split("\n"):
            if "## Feats" in line:
                in_feats_section = True
                continue
            if in_feats_section and line.startswith("## "):
                break
            if in_feats_section:
                m = feat_pattern.match(line)
                if m and m.group(2).strip() != "Feat" and not m.group(2).strip().startswith("-"):
                    level_str = m.group(1)
                    level = int(level_str) if level_str.isdigit() else 1
                    feats.append({
                        "name": m.group(2).strip(),
                        "level_taken": level,
                        "notes": m.group(3).strip(),
                    })
        if feats:
            character_data["feats"] = feats
        else:
            character_data["feats"] = []
            warnings.append("Could not parse feats table")

        # --- Parse Traits table ---
        traits = []
        in_traits_section = False
        trait_pattern = re.compile(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|")
        for line in md_text.split("\n"):
            if "## Traits" in line:
                in_traits_section = True
                continue
            if in_traits_section and line.startswith("## "):
                break
            if in_traits_section:
                m = trait_pattern.match(line)
                if m and m.group(1).strip() != "Trait" and not m.group(1).strip().startswith("-"):
                    traits.append({
                        "name": m.group(1).strip(),
                        "effect": m.group(2).strip(),
                    })
        character_data["traits"] = traits

        # --- Parse Skills table ---
        skills = {}
        in_skills_section = False
        skill_pattern = re.compile(r"\|\s*(.+?)\s*\|\s*[+\-]?\d+\s*\|\s*(\d+)\s*\|")
        for line in md_text.split("\n"):
            if "## Skills" in line:
                in_skills_section = True
                continue
            if in_skills_section and line.startswith("## "):
                break
            if in_skills_section:
                m = skill_pattern.match(line)
                if m and m.group(1).strip() != "Skill" and not m.group(1).strip().startswith("-"):
                    skill_name = m.group(1).strip().lower()
                    ranks = int(m.group(2))
                    if ranks > 0:
                        skills[skill_name] = ranks
        character_data["skills"] = skills

        # --- Parse Equipment list ---
        equipment = []
        in_equip_section = False
        equip_pattern = re.compile(r"^-\s+\*\*(.+?)\*\*(?:\s*\((.+?)\))?")
        for line in md_text.split("\n"):
            if "## Equipment" in line:
                in_equip_section = True
                continue
            if in_equip_section and line.startswith("## "):
                break
            if in_equip_section:
                m = equip_pattern.match(line)
                if m:
                    item = {"name": m.group(1).strip(), "slot": "", "stats": {}}
                    if m.group(2):
                        item["slot"] = m.group(2).strip()
                    equipment.append(item)
        character_data["equipment"] = equipment

        # --- Parse Gold ---
        gold_match = re.search(r"\*\*Gold\*\*:\s*([\d,]+)", md_text)
        if gold_match:
            character_data["gold"] = int(gold_match.group(1).replace(",", ""))
        else:
            character_data["gold"] = 0

        # Fill defaults
        character_data.setdefault("name", "Imported Character")
        character_data.setdefault("race", "")
        character_data.setdefault("classes", [])
        character_data.setdefault("abilities", {
            "str": 10, "dex": 10, "con": 10,
            "int": 10, "wis": 10, "cha": 10,
        })
        character_data.setdefault("spells_known", {})
        character_data.setdefault("spells_prepared", {})
        character_data.setdefault("class_features", [])
        character_data.setdefault("racial_traits", [])
        character_data.setdefault("hp_breakdown", {})
        character_data.setdefault("notes", "Imported from markdown.")

        # Persist the character
        result = persist_character(session_id, player_id, character_data)

        if "error" in result:
            return result

        result["warnings"] = warnings
        return result

    except Exception as e:
        return {"error": str(e), "warnings": warnings}
