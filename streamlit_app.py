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

# Minimal CSS for tighter spacing + print-friendly look and 5e-like cards
st.markdown(
    """
    <style>
      :root{ --accent:#c62828; --ink:#222; --muted:#666; --ring:#f3d6cf; }
      .small-label { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.15rem; }
      .section { border: 1px solid #e6e6e6; border-radius: 14px; padding: 1rem; margin-bottom: 1rem; background: #fafafa; }
      .card { border: 2px solid var(--accent); border-radius: 14px; padding: .8rem; background: #fff; box-shadow: 0 1px 0 rgba(0,0,0,.04) inset; }
      .ability-card { text-align:center; }
      .ability-mod { font-size: 1.8rem; font-weight: 700; line-height: 1; color: var(--ink);}
      .ability-score { font-size: .9rem; color: var(--muted); }
      .pill-label{ font-size:.7rem; color:var(--muted); text-transform:uppercase; letter-spacing:.06em;}
      .big-number{ font-size:1.6rem; font-weight:700;}
      .subgrid{ display:grid; grid-template-columns: repeat(3,1fr); gap:.5rem; }
      .tight > div[data-testid="stVerticalBlock"]{ padding-top:.3rem; padding-bottom:.3rem;}
      .boxed{ border:1px dashed #ddd; border-radius:10px; padding:.5rem;}
      @media (max-width: 1100px){ .subgrid{ grid-template-columns: repeat(2,1fr);} }
      @media print {
        @page { size: A4; margin: 10mm; }
        body { -webkit-print-color-adjust: exact; color-adjust: exact; }
        header, [data-testid="baseButton-secondary"] { display:none !important; }
        .card, .section{ break-inside: avoid; }
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

ABI_MAP = {"STR":"str","DEX":"dex","CON":"con","INT":"int","WIS":"wis","CHA":"cha"}


def ability_total(char, ab_code: str) -> int:
    code = ABI_MAP[ab_code]
    return getattr(char, f"{code}_base") + getattr(char, f"{code}_racial")


def labelled_number(label: str, key: str, value: int = 0, step: int = 1, min_value: int | None = None, max_value: int | None = None):
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    return st.number_input(" ", key=key, value=value, step=step, min_value=min_value, max_value=max_value, label_visibility="collapsed")


def labelled_text(label: str, key: str, value: str = ""):
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    return st.text_input(" ", key=key, value=value, label_visibility="collapsed")


def labelled_select(label: str, key: str, options: List[str], index: int = 0):
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    return st.selectbox(" ", options, index=index if options else None, key=key, label_visibility="collapsed")


def taglist(key: str, label: str, placeholder: str = "Type and press Add"):
    """Simple tags widget without extra dependencies.
    - Adds items via a small form
    - Renders removable chips
    - Stores list in st.session_state[key]
    """
    if key not in st.session_state:
        st.session_state[key] = []

    with st.form(f"{key}_form", clear_on_submit=True):
        val = st.text_input(label, value="", placeholder=placeholder)
        submitted = st.form_submit_button("Add")
    if submitted and val:
        if val not in st.session_state[key]:
            st.session_state[key].append(val)

    tags = list(st.session_state[key])
    if tags:
        n_cols = max(1, min(6, len(tags)))
        cols = st.columns(n_cols)
        for i, t in enumerate(tags):
            col = cols[i % n_cols]
            with col:
                st.button(f"✕ {t}", key=f"{key}_del_{i}", help="Remove",
                          on_click=lambda t=t: st.session_state[key].remove(t))
    return st.session_state[key]

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
    # HP breakdown for 3.5-style tracking
    hp_current: int = 0
    hp_max: int = 0
    hp_temp: int = 0

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

# ---------- Main Page (header + summary) ----------
# Header bar
hdr1, hdr2 = st.columns([1, 5])
with hdr1:
    st.image("https://placehold.co/96x96", caption="Portrait", width=96)
with hdr2:
    st.markdown(f"## {char.name or 'Unnamed'}")
    st.caption(f"{char.race} {char.character_class} · Level {char.level} · Alignment {char.alignment}")

# Ability cards row
st.markdown("#### Abilities")
cols = st.columns(6)
for i, ab in enumerate(["STR","DEX","CON","INT","WIS","CHA"]):
    with cols[i]:
        total = ability_total(char, ab)
        mod = ability_mod(total)
        st.markdown(f"<div class='card ability-card'><div class='pill-label'>{ab}</div><div class='ability-mod'>{mod:+d}</div><div class='ability-score'>{total}</div></div>", unsafe_allow_html=True)

st.markdown("---")
# Status / quick stats row (desktop-first, responsive)
s1, s2, s3, s4 = st.columns([1.2, 1.2, 1.6, 2.4])
with s1:
    st.markdown("**Initiative**")
    ini_total = ability_mod(ability_total(char, "DEX")) + char.initiative_misc
    st.markdown(f"<div class='card' style='text-align:center;'><div class='big-number'>{ini_total:+d}</div><div class='pill-label'>Dex mod + misc</div></div>", unsafe_allow_html=True)
with s2:
    st.markdown("**Speed**")
    st.markdown(f"<div class='card' style='text-align:center;'><div class='big-number'>{char.speed}</div><div class='pill-label'>ft.</div></div>", unsafe_allow_html=True)
with s3:
    st.markdown("**Armor Class**")
    ac_total = 10 + char.ac_armor + char.ac_shield + ability_mod(ability_total(char, "DEX")) + char.ac_natural + char.ac_deflection + char.ac_misc
    st.markdown(f"<div class='card'><div class='big-number' style='text-align:center;'>{ac_total}</div><div class='subgrid'><div class='boxed'>Armor {char.ac_armor}</div><div class='boxed'>Shield {char.ac_shield}</div><div class='boxed'>Dex {ability_mod(ability_total(char, 'DEX')):+d}</div><div class='boxed'>Natural {char.ac_natural}</div><div class='boxed'>Defl. {char.ac_deflection}</div><div class='boxed'>Misc {char.ac_misc}</div></div></div>", unsafe_allow_html=True)
with s4:
    st.markdown("**Hit Points**")
    c = st.columns(3)
    with c[0]: char.hp_current = labelled_number("Current", "hp_current", char.hp_current, min_value=0)
    with c[1]: char.hp_max = labelled_number("Max", "hp_max", max(char.hp_max, char.hp_current))
    with c[2]: char.hp_temp = labelled_number("Temp", "hp_temp", char.hp_temp, min_value=0)
    st.caption("Use Current/Max/Temp for tracking. 'HP' in sidebar is kept for legacy export.")

st.markdown("---")
lcol, mcol, rcol = st.columns([2.4, 3, 2.6])
with lcol:
    st.markdown("**Saving Throws**")
    fort = char.fort_base + ability_mod(ability_total(char, "CON")) + char.save_misc
    ref = char.ref_base + ability_mod(ability_total(char, "DEX")) + char.save_misc
    will = char.will_base + ability_mod(ability_total(char, "WIS")) + char.save_misc
    st.markdown(f"<div class='card'>Fortitude: <b>{fort:+d}</b><br/>Reflex: <b>{ref:+d}</b><br/>Will: <b>{will:+d}</b><br/><span class='pill-label'>(base + ability + misc)</span></div>", unsafe_allow_html=True)

    st.markdown("**Senses**")
    st.text_input("Vision / Notes (e.g., Darkvision 60 ft.)", key="senses_notes")

with mcol:
    st.markdown("**Conditions / Defenses**")
    st.text_input("Active Conditions", key="conditions")
    st.text_input("Defenses (DR/Resistances)", key="defenses")

with rcol:
    st.markdown("**Base Attack Bonus**")
    st.markdown(f"<div class='card' style='text-align:center;'><div class='big-number'>{char.bab:+d}</div></div>", unsafe_allow_html=True)

# ---------- Tabs ----------
tactions, tskills, tfeats, tspells, tgear, tnotes = st.tabs([
    "Actions",
    "Skills",
    "Feats & Features",
    "Spells",
    "Gear & Wealth",
    "Notes & Export",
])

# (Overview tab removed; main page rendered above tabs) 
# (Abilities tab removed; ability editing happens on main page)
# ---------- Actions Tab ----------
with tactions:
    st.markdown("### Actions & Attacks")
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
with tskills:
    st.markdown("### Skills — D&D 3.5 list (editable)")
    SKILLS_35 = [
        ("Appraise","INT"),("Balance","DEX"),("Bluff","CHA"),("Climb","STR"),("Concentration","CON"),
        ("Craft (Alchemy)","INT"),("Craft (Armorsmithing)","INT"),("Craft (Weaponsmithing)","INT"),("Craft (Other)","INT"),
        ("Decipher Script","INT"),("Diplomacy","CHA"),("Disable Device","INT"),("Disguise","CHA"),("Escape Artist","DEX"),
        ("Forgery","INT"),("Gather Information","CHA"),("Handle Animal","CHA"),("Heal","WIS"),("Hide","DEX"),
        ("Intimidate","CHA"),("Jump","STR"),
        ("Knowledge (Arcana)","INT"),("Knowledge (Architecture)","INT"),("Knowledge (Dungeoneering)","INT"),("Knowledge (Geography)","INT"),
        ("Knowledge (History)","INT"),("Knowledge (Local)","INT"),("Knowledge (Nature)","INT"),("Knowledge (Nobility)","INT"),
        ("Knowledge (Religion)","INT"),("Knowledge (The Planes)","INT"),
        ("Listen","WIS"),("Move Silently","DEX"),("Open Lock","DEX"),("Perform","CHA"),("Profession","WIS"),
        ("Ride","DEX"),("Search","INT"),("Sense Motive","WIS"),("Sleight of Hand","DEX"),("Speak Language","—"),
        ("Spellcraft","INT"),("Spot","WIS"),("Survival","WIS"),("Swim","STR"),("Tumble","DEX"),("Use Magic Device","CHA"),("Use Rope","DEX")
    ]
    if st.session_state.get("skills_table") is None or st.session_state.get("skills_table_seed") != "3.5":
        st.session_state.skills_table = [
            {"Skill": s, "Ability": ab, "Ranks": 0, "Misc": 0, "Class": True} for s, ab in SKILLS_35
        ]
        st.session_state.skills_table_seed = "3.5"

    edited = st.data_editor(
        st.session_state.skills_table,
        num_rows="dynamic",
        use_container_width=True,
        key="skills_editor",
        column_config={"Class": st.column_config.CheckboxColumn("Class Skill")},
    )
    st.session_state.skills_table = edited

# ---------- Feats & Features Tab ----------
with tfeats:
    st.markdown("### Feats & Class Features")
    feats = taglist("feats_tags", "Feats (type and press Add)")
    features = taglist("features_tags", "Class Features")
    st.caption("These will later be validated against prerequisites from the database.")

# ---------- Spells Tab ----------
with tspells:
    st.markdown("### Spells")
    cls = char.character_class
    st.write("Casting Class:", cls)
    st.selectbox("Spell List Level", options=list(range(0, 10)), key="spell_level")
    taglist("spells_known", "Known/Prepared Spells")
    st.text_area("Spellbook / Notes", key="spellbook_notes")

# ---------- Gear & Wealth Tab ----------
with tgear:
    st.markdown("### Gear & Wealth")
    taglist("languages", "Languages")
    st.text_area("Weapons & Armor", key="gear_weapons", height=100)
    st.text_area("Equipment & Tools", key="gear_tools", height=120)
    st.number_input("Wealth (gp)", key="wealth_gp", value=0, step=1)

# ---------- Notes & Export Tab ----------
with tnotes:
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

    st.caption("For a print-friendly sheet, use the browser print dialog on the Main page and Actions tab.")
