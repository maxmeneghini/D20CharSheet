# app.py
# D&D 3.5 Character Builder – UI Skeleton (Streamlit)
# Run locally:  streamlit run app.py

import json
from dataclasses import dataclass, asdict
from typing import Dict, List

import streamlit as st

# ---------- Page setup ----------
st.set_page_config(
    page_title="D&D 3.5 Character Builder",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal CSS for tighter spacing + print-friendly look
st.markdown(
    """
    <style>
      .small-label { font-size: 0.85rem; color: #555; margin-bottom: 0.15rem; }
      .stat-box { border: 1px solid #ddd; border-radius: 10px; padding: 0.65rem; background: #fff; }
      .section { border: 1px solid #e6e6e6; border-radius: 14px; padding: 1rem; margin-bottom: 1rem; background: #fafafa; }
      @media print {
        section.main > div { padding-top: 0 !important; }
        header { display: none; }
        .stButton>button { display: none; }
        .section { break-inside: avoid; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------

def ability_mod(score: int) -> int:
    try:
        return (int(score) - 10) // 2
    except Exception:
        return 0


def labelled_number(label: str, key: str, value: int = 0, step: int = 1, min_value: int | None = None, max_value: int | None = None):
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    return st.number_input(" ", key=key, value=value, step=step, min_value=min_value, max_value=max_value, label_visibility="collapsed")


def labelled_text(label: str, key: str, value: str = ""):
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    return st.text_input(" ", key=key, value=value, label_visibility="collapsed")


def labelled_select(label: str, key: str, options: List[str], index: int = 0):
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    return st.selectbox(" ", options, index=index if options else None, key=key, label_visibility="collapsed")


@dataclass
class Character:
    name: str = ""
    player: str = ""
    alignment: str = "Neutral"
    deity: str = ""
    size: str = "Medium"
    race: str = "Human"
    character_class: str = "Fighter"
    level: int = 1
    xp: int = 0
    age: int = 18
    gender: str = ""
    height: str = ""
    weight: str = ""
    eyes: str = ""
    hair: str = ""
    skin: str = ""

    # Abilities
    str_base: int = 10
    dex_base: int = 10
    con_base: int = 10
    int_base: int = 10
    wis_base: int = 10
    cha_base: int = 10
    # Racial adjustments (to be auto-filled from DB later)
    str_racial: int = 0
    dex_racial: int = 0
    con_racial: int = 0
    int_racial: int = 0
    wis_racial: int = 0
    cha_racial: int = 0

    # Combat basics
    hp: int = 0
    hit_die: str = "d10"
    bab: int = 0
    ac_armor: int = 0
    ac_shield: int = 0
    ac_natural: int = 0
    ac_deflection: int = 0
    ac_misc: int = 0
    initiative_misc: int = 0

    # Saves (base values will come from class table)
    fort_base: int = 0
    ref_base: int = 0
    will_base: int = 0
    save_misc: int = 0

    # Movement
    speed: int = 30

    # Lists (placeholder; wire to DB later)
    feats: List[str] = None
    class_features: List[str] = None
    skills: Dict[str, Dict[str, int]] = None
    languages: List[str] = None


if "char" not in st.session_state:
    st.session_state.char = Character()

char: Character = st.session_state.char

# ---------- Sidebar: core identity ----------
st.sidebar.header("Character Meta")
char.name = labelled_text("Name", "name", char.name)
char.player = labelled_text("Player", "player", char.player)
char.alignment = labelled_select(
    "Alignment",
    "alignment",
    [
        "LG", "NG", "CG",
        "LN", "N", "CN",
        "LE", "NE", "CE",
    ],
    index=4,
)

# These will later be DB-driven
race_options = ["Human", "Elf", "Dwarf", "Gnome", "Halfling", "Half-Orc", "Half-Elf"]
class_options = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Wizard"
]
char.race = labelled_select("Race", "race", race_options, index=race_options.index(char.race) if char.race in race_options else 0)
char.character_class = labelled_select(
    "Class", "class", class_options, index=class_options.index(char.character_class) if char.character_class in class_options else 4
)
char.level = labelled_number("Level", "level", max(1, char.level), min_value=1, max_value=20)
char.xp = labelled_number("XP", "xp", char.xp, step=100)

st.sidebar.divider()
st.sidebar.subheader("Physical")
char.age = labelled_number("Age", "age", char.age, min_value=1)
char.gender = labelled_text("Gender", "gender", char.gender)
char.height = labelled_text("Height", "height", char.height)
char.weight = labelled_text("Weight", "weight", char.weight)
char.eyes = labelled_text("Eyes", "eyes", char.eyes)
char.hair = labelled_text("Hair", "hair", char.hair)
char.skin = labelled_text("Skin", "skin", char.skin)

# ---------- Header ----------
st.title("D&D 3.5 Character Sheet (UI Skeleton)")
st.caption("Start with layout; wire rules & database later. All fields are local session state.")

# ---------- Tabs ----------
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "Overview",
    "Abilities",
    "Combat",
    "Skills",
    "Feats & Features",
    "Spells",
    "Gear & Wealth",
    "Notes & Export",
])

# ---------- Overview Tab ----------
with t1:
    st.markdown("### Overview")
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        labelled_text("Deity", "deity", char.deity)
        labelled_text("Size", "size", char.size)
        labelled_number("Speed (ft)", "speed", char.speed, step=5)
    with c2:
        labelled_text("Hit Die", "hit_die", char.hit_die)
        labelled_number("HP", "hp", char.hp)
        labelled_number("Initiative (misc)", "initiative_misc", char.initiative_misc)
    with c3:
        labelled_number("BAB", "bab", char.bab)
        labelled_number("Fort Base", "fort_base", char.fort_base)
        labelled_number("Ref Base", "ref_base", char.ref_base)
    with c4:
        labelled_number("Will Base", "will_base", char.will_base)
        labelled_number("Save Misc (all)", "save_misc", char.save_misc)

    st.markdown("### Armor Class (AC)")
    ac1, ac2, ac3, ac4, ac5 = st.columns(5)
    with ac1:
        labelled_number("Armor", "ac_armor", char.ac_armor)
    with ac2:
        labelled_number("Shield", "ac_shield", char.ac_shield)
    with ac3:
        labelled_number("Natural", "ac_natural", char.ac_natural)
    with ac4:
        labelled_number("Deflection", "ac_deflection", char.ac_deflection)
    with ac5:
        labelled_number("Misc", "ac_misc", char.ac_misc)

# ---------- Abilities Tab ----------
with t2:
    st.markdown("### Ability Scores")
    grid = st.columns(6)
    labels = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    base_keys = ["str_base", "dex_base", "con_base", "int_base", "wis_base", "cha_base"]
    racial_keys = ["str_racial", "dex_racial", "con_racial", "int_racial", "wis_racial", "cha_racial"]

    for i, (lab, base_k, racial_k) in enumerate(zip(labels, base_keys, racial_keys)):
        with grid[i]:
            st.markdown(f"**{lab}**")
            base = labelled_number("Base", base_k, getattr(char, base_k), min_value=1, max_value=30)
            racial = labelled_number("Racial Adj", racial_k, getattr(char, racial_k), min_value=-10, max_value=10)
            total = int(base) + int(racial)
            mod = ability_mod(total)
            st.markdown(
                f"<div class='stat-box'>Total: <b>{total}</b><br/>Mod: <b>{mod:+d}</b></div>",
                unsafe_allow_html=True,
            )
            setattr(char, base_k, base)
            setattr(char, racial_k, racial)

# ---------- Combat Tab ----------
with t3:
    st.markdown("### Attacks")
    a1, a2, a3 = st.columns(3)
    with a1:
        labelled_text("Primary Weapon", "wpn1", "Longsword")
        labelled_text("Attack Bonus", "wpn1_atk", "+0")
        labelled_text("Damage", "wpn1_dmg", "1d8/")
    with a2:
        labelled_text("Secondary Weapon", "wpn2", "Shortbow")
        labelled_text("Attack Bonus", "wpn2_atk", "+0")
        labelled_text("Damage", "wpn2_dmg", "1d6/")
    with a3:
        labelled_text("Melee Notes", "melee_notes", "")
        labelled_text("Ranged Notes", "ranged_notes", "")

    st.markdown("### Saving Throws (computed later)")
    s1, s2, s3 = st.columns(3)
    for label, base_key in [("Fortitude", "fort_base"), ("Reflex", "ref_base"), ("Will", "will_base")]:
        with s1 if label == "Fortitude" else s2 if label == "Reflex" else s3:
            base = getattr(char, base_key)
            st.write({
                "Base": base,
                "Ability": {
                    "Fortitude": ability_mod(char.con_base + char.con_racial),
                    "Reflex": ability_mod(char.dex_base + char.dex_racial),
                    "Will": ability_mod(char.wis_base + char.wis_racial),
                }[label],
                "Magic": 0,
                "Misc": char.save_misc,
                "Temp": 0,
            })

# ---------- Skills Tab ----------
with t4:
    st.markdown("### Skills (placeholder table; wire to DB)")
    # A tiny starter skill list; replace with DB lookup
    if st.session_state.get("skills_table") is None:
        st.session_state.skills_table = [
            {"Skill": "Balance", "Ability": "DEX", "Ranks": 0, "Misc": 0, "Class": True},
            {"Skill": "Climb", "Ability": "STR", "Ranks": 0, "Misc": 0, "Class": True},
            {"Skill": "Concentration", "Ability": "CON", "Ranks": 0, "Misc": 0, "Class": True},
            {"Skill": "Hide", "Ability": "DEX", "Ranks": 0, "Misc": 0, "Class": False},
            {"Skill": "Move Silently", "Ability": "DEX", "Ranks": 0, "Misc": 0, "Class": False},
            {"Skill": "Spellcraft", "Ability": "INT", "Ranks": 0, "Misc": 0, "Class": False},
        ]
    st.session_state.skills_table = st.data_editor(
        st.session_state.skills_table,
        num_rows="dynamic",
        use_container_width=True,
        key="skills_editor",
    )

# ---------- Feats & Features Tab ----------
with t5:
    st.markdown("### Feats & Class Features")
    feats = st.tags_input("Feats (type and press Enter)", key="feats_tags")
    features = st.tags_input("Class Features", key="features_tags")
    st.caption("These will later be validated against prerequisites from the database.")

# ---------- Spells Tab ----------
with t6:
    st.markdown("### Spells")
    cls = char.character_class
    st.write("Casting Class:", cls)
    st.selectbox("Spell List Level", options=list(range(0, 10)), key="spell_level")
    st.tags_input("Known/Prepared Spells", key="spells_known")
    st.text_area("Spellbook / Notes", key="spellbook_notes")

# ---------- Gear & Wealth Tab ----------
with t7:
    st.markdown("### Gear & Wealth")
    st.tags_input("Languages", key="languages")
    st.text_area("Weapons & Armor", key="gear_weapons", height=100)
    st.text_area("Equipment & Tools", key="gear_tools", height=120)
    st.number_input("Wealth (gp)", key="wealth_gp", value=0, step=1)

# ---------- Notes & Export Tab ----------
with t8:
    st.markdown("### Notes")
    st.text_area("Background & Personality", key="notes_bg", height=180)
    st.text_area("Allies & Organizations", key="notes_allies", height=120)
    st.text_area("Other Notes", key="notes_other", height=120)

    st.divider()
    st.markdown("### Export")

    # Construct a serializable dict for export
    export_dict = asdict(char)
    export_dict.update({
        "feats": st.session_state.get("feats_tags", []),
        "class_features": st.session_state.get("features_tags", []),
        "skills_table": st.session_state.get("skills_table", []),
        "spells_known": st.session_state.get("spells_known", []),
        "spellbook_notes": st.session_state.get("spellbook_notes", ""),
        "languages": st.session_state.get("languages", []),
        "gear": {
            "weapons": st.session_state.get("gear_weapons", ""),
            "tools": st.session_state.get("gear_tools", ""),
            "wealth_gp": st.session_state.get("wealth_gp", 0),
        },
        "notes": {
            "background": st.session_state.get("notes_bg", ""),
            "allies": st.session_state.get("notes_allies", ""),
            "other": st.session_state.get("notes_other", ""),
        },
    })

    st.download_button(
        "Download Character (JSON)",
        data=json.dumps(export_dict, indent=2),
        file_name=f"{char.name or 'character'}.json",
        mime="application/json",
    )

    st.caption("For a print-friendly sheet, use the browser print dialog on the Overview/Abilities/Combat tabs.")
