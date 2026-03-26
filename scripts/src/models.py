"""
Normalized Pathfinder 1e Game Data Types.
Canonical output format for all scraped/extracted data regardless of source.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


# === Classes ===

@dataclass
class ClassProgression:
    level: int
    bab: int
    fort: int
    ref: int
    will: int
    special: list[str] = field(default_factory=list)


@dataclass
class SpellCasting:
    type: str  # arcane, divine, psychic, alchemist
    spontaneous: bool
    casting_ability: str  # CHA, INT, WIS
    spells_per_day: Optional[list[list[int | None]]] = None  # [class_level][spell_level]
    spells_known: Optional[list[list[int | None]]] = None


@dataclass
class ClassFeature:
    name: str
    level: int
    description: str
    ability_type: Optional[str] = None  # Ex, Su, Sp


@dataclass
class PrestigeRequirement:
    type: str  # bab, skills, feats, spells, special, alignment
    text: str = ""
    value: int = 0
    items: list[str] = field(default_factory=list)


@dataclass
class BaseClass:
    name: str
    source: str
    description: str
    hit_die: int
    skill_ranks_per_level: int
    class_skills: list[str] = field(default_factory=list)
    progression: list[ClassProgression] = field(default_factory=list)
    class_features: list[ClassFeature] = field(default_factory=list)
    spellcasting: Optional[SpellCasting] = None
    role: Optional[str] = None
    alignment: Optional[str] = None
    starting_wealth: Optional[str] = None
    requirements: list[PrestigeRequirement] = field(default_factory=list)


# === Archetypes ===

@dataclass
class ArchetypeFeature:
    name: str
    description: str
    ability_type: Optional[str] = None  # Ex, Su, Sp


@dataclass
class ArchetypeModification:
    """
    How an archetype changes the base class:
    - 'replace': removes a class feature and adds a new one
    - 'alter': modifies an existing class feature
    - 'add': adds a new feature without removing anything
    """
    type: str  # replace, alter, add
    replaces: Optional[str] = None  # class feature name being replaced/altered
    levels: Optional[list[int]] = None
    feature: Optional[ArchetypeFeature] = None


@dataclass
class Archetype:
    name: str
    base_class: str
    source: str
    description: str
    modifications: list[ArchetypeModification] = field(default_factory=list)
    replaced_features: list[str] = field(default_factory=list)


# === Races ===

@dataclass
class RacialTrait:
    name: str
    description: str
    ability_type: Optional[str] = None


@dataclass
class AlternateRacialTrait:
    name: str
    description: str
    replaces: list[str] = field(default_factory=list)


@dataclass
class Race:
    name: str
    source: str
    description: str
    type: str  # humanoid, outsider, etc.
    subtypes: list[str] = field(default_factory=list)
    size: str = "Medium"
    speed: list[dict] = field(default_factory=list)  # [{"type": "land", "value": 30}]
    ability_modifiers: list[dict] = field(default_factory=list)  # [{"ability": "DEX", "modifier": 2}]
    languages: dict = field(default_factory=lambda: {"starting": [], "bonus": []})
    racial_traits: list[RacialTrait] = field(default_factory=list)
    alternate_racial_traits: list[AlternateRacialTrait] = field(default_factory=list)


# === Skills ===

@dataclass
class Skill:
    name: str
    ability: str  # STR, DEX, CON, INT, WIS, CHA
    trained_only: bool = False
    armor_check_penalty: bool = False
    description: str = ""


# === Spells ===

@dataclass
class SpellClassLevel:
    class_name: str
    level: int


@dataclass
class Spell:
    name: str
    school: str
    source: str
    class_levels: list[SpellClassLevel] = field(default_factory=list)
    subschool: Optional[str] = None
    descriptors: list[str] = field(default_factory=list)
    casting_time: str = ""
    components: str = ""
    range: str = ""
    target: Optional[str] = None
    area: Optional[str] = None
    effect: Optional[str] = None
    duration: str = ""
    saving_throw: str = ""
    spell_resistance: str = ""
    description: str = ""
    url: Optional[str] = None


# === Feats ===

@dataclass
class ParsedPrerequisite:
    type: str  # ability, bab, caster_level, skill, class_level, class_feature, feat, special
    name: str = ""
    value: int = 0
    detail: str = ""


@dataclass
class Feat:
    name: str
    source: str
    types: list[str] = field(default_factory=list)  # Combat, General, Metamagic, etc.
    prerequisites: str = ""
    benefit: str = ""
    normal: Optional[str] = None
    special: Optional[str] = None
    url: Optional[str] = None
    parsed_prerequisites: list[ParsedPrerequisite] = field(default_factory=list)


# === Items ===

@dataclass
class MagicItem:
    name: str
    source: str
    category: str  # wondrous, weapon, armor, shield, ring, rod, staff, potion, etc.
    price: str = ""
    slot: Optional[str] = None
    aura: Optional[str] = None
    caster_level: Optional[int] = None
    weight: Optional[str] = None
    description: str = ""
    construction_requirements: Optional[str] = None
    construction_cost: Optional[str] = None
    url: Optional[str] = None


# === Equipment (Mundane) ===

@dataclass
class WeaponStats:
    damage_medium: str = ""
    damage_small: str = ""
    critical: str = ""
    damage_type: str = ""
    range_increment: str = ""
    proficiency: str = ""
    weapon_class: str = ""
    special: str = ""


@dataclass
class ArmorStats:
    armor_bonus: int = 0
    shield_bonus: int = 0
    max_dex_bonus: Optional[int] = None
    armor_check_penalty: int = 0
    arcane_spell_failure: int = 0
    speed_30: Optional[str] = None
    speed_20: Optional[str] = None


@dataclass
class Equipment:
    name: str
    source: str
    category: str  # weapon, armor, shield, gear
    price: str = ""
    weight: str = ""
    description: str = ""
    weapon_stats: Optional[WeaponStats] = None
    armor_stats: Optional[ArmorStats] = None


# === Class Options (Domains, Bloodlines, etc.) ===

@dataclass
class DomainSpellEntry:
    level: int
    spell_name: str


@dataclass
class Domain:
    name: str
    source: str
    description: str = ""
    granted_powers: str = ""
    spells: list[DomainSpellEntry] = field(default_factory=list)


@dataclass
class Subdomain:
    name: str
    domain: str
    source: str
    description: str = ""
    replaced_powers: str = ""
    replacement_powers: str = ""


@dataclass
class Bloodline:
    name: str
    source: str
    description: str = ""
    class_skill: str = ""
    bonus_spells: list[DomainSpellEntry] = field(default_factory=list)
    bonus_feats: str = ""
    bloodline_arcana: str = ""
    bloodline_powers: str = ""


@dataclass
class OracleMystery:
    name: str
    source: str
    description: str = ""
    class_skills: list[str] = field(default_factory=list)
    bonus_spells: list[DomainSpellEntry] = field(default_factory=list)
    revelations: str = ""


@dataclass
class WitchPatron:
    name: str
    source: str
    spells: list[DomainSpellEntry] = field(default_factory=list)


# === Aggregate Output ===

@dataclass
class GameData:
    classes: list[BaseClass] = field(default_factory=list)
    archetypes: list[Archetype] = field(default_factory=list)
    races: list[Race] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    spells: list[Spell] = field(default_factory=list)
    feats: list[Feat] = field(default_factory=list)
    items: list[MagicItem] = field(default_factory=list)


def to_json(obj, indent=2) -> str:
    """Serialize any dataclass to JSON."""
    return json.dumps(asdict(obj), indent=indent, ensure_ascii=False)


def save_json(data, path: str):
    """Save a dataclass (or list of dataclasses) to a JSON file."""
    if isinstance(data, list):
        serialized = [asdict(item) for item in data]
    else:
        serialized = asdict(data)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)
    print(f"  Saved {path} ({len(serialized) if isinstance(serialized, list) else 'object'})")
