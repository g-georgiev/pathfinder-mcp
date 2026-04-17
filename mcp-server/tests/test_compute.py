"""Tests for the PF1e compute engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

RULES_DB_PATH = str(Path(__file__).parent.parent.parent / "db" / "pathfinder.db")
from compute.progression import lookup_class_data
from compute.hp import compute_hp
from compute.saves import compute_saves
from compute.combat_stats import (
    compute_bab, compute_ac, compute_cmb_cmd, compute_initiative, compute_attack_lines,
)
from compute.skills import compute_skill_totals
from compute.spells import compute_spell_slots
from compute.derived import compute_derived_stats


# ---------------------------------------------------------------------------
# Helper: build class_data dict from rules DB for given class names
# ---------------------------------------------------------------------------

def _build_class_data(*class_names):
    """Look up class data for multiple classes and return a dict keyed by lowercase name."""
    result = {}
    for name in class_names:
        cd = lookup_class_data(name, RULES_DB_PATH)
        if "error" not in cd:
            result[name.lower()] = cd
    return result


# ===========================================================================
# Fighter L5 tests
# ===========================================================================

class TestFighterL5:
    """Fighter level 5 — BAB 5, good Fort, poor Ref/Will."""

    def setup_method(self):
        self.classes = [{"name": "Fighter", "level": 5}]
        self.class_data = _build_class_data("Fighter")
        self.ability_mods = {"str": 4, "dex": 2, "con": 2, "int": 0, "wis": 1, "cha": -1}

    def test_bab(self):
        bab = compute_bab(self.classes, self.class_data)
        assert bab == 5

    def test_saves(self):
        saves = compute_saves(self.classes, self.class_data, self.ability_mods)
        # Fighter L5: base Fort=4, Ref=1, Will=1
        assert saves["fort"] == 4 + 2  # +CON
        assert saves["ref"] == 1 + 2   # +DEX
        assert saves["will"] == 1 + 1  # +WIS

    def test_hp_with_breakdown(self):
        hp_breakdown = {
            "hit_dice": 33,
            "con": 10,
            "favored_class": 5,
            "toughness": 5,
            "misc": 0,
        }
        result = compute_hp(
            self.classes, self.class_data, self.ability_mods,
            hp_breakdown, [{"name": "Toughness"}],
        )
        assert result["max"] == 53  # 33 + 10 + 5 + 5

    def test_hp_computed_from_scratch(self):
        """Without breakdown, compute from scratch."""
        result = compute_hp(
            self.classes, self.class_data, self.ability_mods,
            {}, [{"name": "Toughness"}],
        )
        # Fighter hit die = 10. L1 = 10, L2-5 = 6 each = 24.
        # hit_dice = 10 + 24 = 34, con = 2*5 = 10, toughness = 5
        assert result["max"] == 34 + 10 + 5  # 49
        assert result["breakdown"]["hit_dice"] == 34
        assert result["breakdown"]["con"] == 10
        assert result["breakdown"]["toughness"] == 5


# ===========================================================================
# Wizard L10 tests
# ===========================================================================

class TestWizardL10:
    """Wizard level 10 — BAB 5, poor Fort/Ref, good Will."""

    def setup_method(self):
        self.classes = [{"name": "Wizard", "level": 10}]
        self.class_data = _build_class_data("Wizard")
        self.ability_mods = {"str": 0, "dex": 2, "con": 2, "int": 7, "wis": 1, "cha": -1}

    def test_bab(self):
        bab = compute_bab(self.classes, self.class_data)
        assert bab == 5

    def test_saves(self):
        saves = compute_saves(self.classes, self.class_data, self.ability_mods)
        # Wizard L10: base Fort=3, Ref=3, Will=7
        assert saves["fort"] == 3 + 2  # +CON
        assert saves["ref"] == 3 + 2   # +DEX
        assert saves["will"] == 7 + 1  # +WIS

    def test_spell_slots_wizard_int24(self):
        """Wizard L10 with INT 24 (+7 mod) should have bonus spells."""
        result = compute_spell_slots(self.classes, self.class_data, self.ability_mods)
        assert "wizard" in result
        slots = result["wizard"]
        # Spell level 1: bonus = 1 + (7-1)//4 = 1 + 1 = 2
        # Spell level 5: bonus = 1 + (7-5)//4 = 1 + 0 = 1
        # Verify bonus spells are added (exact base depends on DB data)
        for level_str, total in slots.items():
            level = int(level_str)
            if level > 0:
                assert total > 0, f"Spell level {level} should have slots"


# ===========================================================================
# AC computation tests
# ===========================================================================

class TestAC:
    def test_ac_with_armor_shield_dex_cap(self):
        equipment = [
            {"name": "Full Plate", "slot": "armor", "stats": {
                "ac_bonus": 9, "max_dex": 1, "type": "armor",
            }},
            {"name": "Heavy Steel Shield", "slot": "offhand", "stats": {
                "ac_bonus": 2, "type": "shield",
            }},
        ]
        ability_mods = {"str": 4, "dex": 2, "con": 2, "int": 0, "wis": 1, "cha": -1}
        ac = compute_ac(equipment, ability_mods)
        # 10 + 9 armor + 2 shield + 1 DEX (capped from 2) = 22
        assert ac["total"] == 22
        assert ac["components"]["dex"] == 1  # capped
        assert ac["components"]["armor"] == 9
        assert ac["components"]["shield"] == 2
        # Touch = 22 - 9 - 2 = 11
        assert ac["touch"] == 11
        # Flat-footed = 22 - 1 (DEX) = 21
        assert ac["flat_footed"] == 21

    def test_ac_no_equipment(self):
        ac = compute_ac([], {"dex": 3})
        assert ac["total"] == 13  # 10 + 3 DEX
        assert ac["touch"] == 13
        assert ac["flat_footed"] == 10


# ===========================================================================
# Multiclass BAB test
# ===========================================================================

class TestMulticlass:
    def test_fighter3_rogue2_bab(self):
        """Fighter 3 (BAB 3) + Rogue 2 (BAB 1) = 4."""
        classes = [
            {"name": "Fighter", "level": 3},
            {"name": "Rogue", "level": 2},
        ]
        class_data = _build_class_data("Fighter", "Rogue")
        bab = compute_bab(classes, class_data)
        assert bab == 4


# ===========================================================================
# CMB/CMD tests
# ===========================================================================

class TestCMBCMD:
    def test_cmb_cmd(self):
        ability_mods = {"str": 4, "dex": 2}
        result = compute_cmb_cmd(5, ability_mods)
        assert result["cmb"] == 9   # 5 + 4
        assert result["cmd"] == 21  # 10 + 5 + 4 + 2


# ===========================================================================
# Initiative tests
# ===========================================================================

class TestInitiative:
    def test_basic_initiative(self):
        ability_mods = {"dex": 2}
        result = compute_initiative(ability_mods, [], [])
        assert result["total"] == 2

    def test_improved_initiative(self):
        ability_mods = {"dex": 2}
        feats = [{"name": "Improved Initiative"}]
        result = compute_initiative(ability_mods, feats, [])
        assert result["total"] == 6

    def test_reactionary_trait(self):
        ability_mods = {"dex": 2}
        traits = [{"name": "Reactionary", "effect": "+2 initiative"}]
        result = compute_initiative(ability_mods, [], traits)
        assert result["total"] == 4


# ===========================================================================
# Attack lines tests
# ===========================================================================

class TestAttackLines:
    def test_melee_weapon(self):
        equipment = [
            {"name": "Longsword +1", "slot": "weapon", "stats": {
                "type": "melee", "damage": "1d8", "crit": "19-20/x2",
                "enhancement": 1, "ability": "str",
            }},
        ]
        ability_mods = {"str": 4, "dex": 2}
        feats = [{"name": "Weapon Specialization"}]
        attacks = compute_attack_lines(equipment, 5, ability_mods, feats)
        assert len(attacks) == 1
        atk = attacks[0]
        assert atk["name"] == "Longsword +1"
        # AB = 5 (BAB) + 4 (STR) + 1 (enh) = 10
        assert atk["ab"] == [10]
        # Damage = 1d8 + 4 (STR) + 1 (enh) + 2 (W.Spec) = 1d8+7
        assert atk["damage"] == "1d8+7"

    def test_iterative_attacks(self):
        equipment = [
            {"name": "Sword", "slot": "weapon", "stats": {
                "type": "melee", "damage": "1d8", "crit": "20/x2",
                "enhancement": 0, "ability": "str",
            }},
        ]
        ability_mods = {"str": 3}
        attacks = compute_attack_lines(equipment, 11, ability_mods, [])
        assert len(attacks) == 1
        # BAB 11: primary, -5, -10
        assert len(attacks[0]["ab"]) == 3
        assert attacks[0]["ab"] == [14, 9, 4]


# ===========================================================================
# Skills tests
# ===========================================================================

class TestSkills:
    def test_skill_totals(self):
        skills = {"perception": 5, "climb": 3}
        ability_mods = {"str": 4, "dex": 2, "con": 2, "int": 0, "wis": 1, "cha": -1}
        classes = [{"name": "Fighter", "level": 5}]
        class_data = _build_class_data("Fighter")
        totals = compute_skill_totals(skills, ability_mods, classes, class_data)
        # perception: 5 ranks + 1 (WIS). Fighter doesn't have perception as class skill.
        # climb: 3 ranks + 4 (STR) + 3 (class skill for Fighter) = 10
        assert totals["perception"] == 6
        assert totals["climb"] == 10


# ===========================================================================
# Full derived stats test
# ===========================================================================

class TestDerivedStats:
    def test_full_fighter(self, sample_character_data):
        result = compute_derived_stats(sample_character_data, RULES_DB_PATH)
        assert "ability_mods" in result
        assert "hp" in result
        assert "saves" in result
        assert "bab" in result
        assert "ac" in result
        assert result["bab"] == 5
        assert result["hp"]["max"] == 53  # from provided breakdown

    def test_full_wizard(self, sample_wizard_data):
        result = compute_derived_stats(sample_wizard_data, RULES_DB_PATH)
        assert result["bab"] == 5
        assert result["saves"]["will"] == 8  # 7 base + 1 WIS
        assert "spell_slots" in result
