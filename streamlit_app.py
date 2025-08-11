# app.py — D&D 3.5 Character Builder (UI Skeleton, compact HP card)
# Run: streamlit run app.py

import json
from dataclasses import dataclass, asdict
from typing import Dict, List
import streamlit as st

# ---------- Page ----------
st.set_page_config(page_title="D&D 3.5 Character Builder", layout="wide", initial_sidebar_state="expanded")

# ---------- Styles (global + HP compact) ----------
st.markdown(
    """
    <style>
      :root{ --accent:#c62828; --ink:#222; --muted:#666; }
      .small-label { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.15rem; }
      .section { border: 1px solid #e6e6e6; border-radius: 14px; padding: .6rem; margin-bottom: .6rem; background: #fafafa; }
      .card { border: 2px solid var(--accent); border-radius: 12px; padding: .6rem; background: #fff; color:#000; box-shadow: 0 1px 0 rgba(0,0,0,.04) inset; }
      .card * { color:#000; }
      .ability-card { text-align:center; }
      .ability-mod { font-size: 1.4rem; font-weight: 700; line-height: 1; }
      .ability-score { font-size: .8rem; color: var(--muted); }
      .pill-label{ font-size:.75rem; color:#444; text-transform:uppercase; letter-spacing:.06em;}
      .big-number{ font-size:1.8rem; font-weight:700;}
      .subgrid{ display:grid; grid-template-columns: repeat(2,1fr); gap:.4rem; }
      @media print { @page { size: A4; margin: 10mm; } header,[data-testid="baseButton-secondary"]{display:none!important} .card{break-inside:avoid} }

      /* Make Streamlit bordered containers render like white cards */
      div[data-testid="stVerticalBlockBorderWrapper"]{ background:#fff; border:2px solid var(--accent); border-radius:12px; padding:.45rem; }
      div[data-testid="stVerticalBlockBorderWrapper"] *{ color:#000; }

      /* HP Card Compact Styling */
      .hp-card div[data-testid="stVerticalBlockBorderWrapper"] { padding: .2rem !important; }
      .hp-card .hp-first .stButton>button { padding: .1rem .25rem; font-size: .7rem; height: 24px; line-height: 1; }
      .hp-card .hp-first div[data-testid="stNumberInput"] input { height: 24px; font-size: .75rem; padding: 1px 4px; }
      .hp-card .hp-first [data-testid="stVerticalBlock"] { padding-top: .1rem !important; padding-bottom: .1rem !important; margin: 0 !important; }
      .hp-card .hp-mid .labels { justify-content: center; gap: 2rem; font-size: .9rem; letter-spacing:.06em; text-transform:uppercase; color:#333; }
      .hp-card .hp-mid .hp-footer { font-size: 1.1rem; font-weight: 700; text-align: center; margin-top: .1rem; text-transform:uppercase; }
      .hp-card .hp-mid .big-number{ font-size:1.7rem; }
      .hp-card .hp-side input { height: 24px !important; font-size: .75rem !important; padding: 1px 4px !important; }
      .hp-card .hp-side .small-label { font-size: .7rem; margin-bottom: .05rem; }
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
                st.button(f"✕ {t}", key=f"{key}_del_{i}", help="Remove", on_click=lambda t=t: st.session_state[key].remove(t))
    return st.session_state[key]

# ---------- Data Model ----------
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
    str_base: int = 10; dex_base: int = 10; con_base: int = 10
    int_base: int = 10; wis_base: int = 10; cha_base: int = 10
    str_racial: int = 0; dex_racial: int = 0; con_racial: int = 0
    int_racial: int = 0; wis_racial: int = 0; cha_racial: int = 0

    # Combat basics
    hp: int = 0
    hit_die: str = "d10"
    bab: int = 0
    ac_armor: int = 0; ac_shield: int = 0; ac_natural: int = 0; ac_deflection: int = 0; ac_misc: int = 0
    initiative_misc: int = 0
    hp_current: int = 0; hp_max: int = 0; hp_temp: int = 0

    # Saves
    fort_base: int = 0; ref_base: int = 0; will_base: int = 0; save_misc: int = 0

    # Movement
    speed: int = 30

    # Lists (placeholder)
    feats: List[str] = None
    class_features: List[str] = None
    skills: Dict[str, Dict[str, int]] = None
    languages: List[str] = None

if "char" not in st.session_state:
    st.session_state.char = Character()
char: Character = st.session_state.char

# ---------- Sidebar ----------
st.sidebar.header("Character Meta")
char.name = labelled_text("Name", "name", char.name)
char.player = labelled_text("Player", "player", char.player)
char.alignment = labelled_select("Alignment", "alignment", ["LG","NG","CG","LN","N","CN","LE","NE","CE"], index=4)

race_options = ["Human","Elf","Dwarf","Gnome","Halfling","Half-Orc","Half-Elf"]
class_options = ["Barbarian","Bard","Cleric","Druid","Fighter","Monk","Paladin","Ranger","Rogue","Sorcerer","Wizard"]
char.race = labelled_select("Race","race",race_options,index=race_options.index(char.race) if char.race in race_options else 0)
char.character_class = labelled_select("Class","class",class_options,index=class_options.index(char.character_class) if char.character_class in class_options else 4)
char.level = labelled_number("Level","level",max(1,char.level),min_value=1,max_value=20)
char.xp = labelled_number("XP","xp",char.xp,step=100)

st.sidebar.divider()
st.sidebar.subheader("Physical")
char.age = labelled_number("Age","age",char.age,min_value=1)
char.gender = labelled_text("Gender","gender",char.gender)
char.height = labelled_text("Height","height",char.height)
char.weight = labelled_text("Weight","weight",char.weight)
char.eyes = labelled_text("Eyes","eyes",char.eyes)
char.hair = labelled_text("Hair","hair",char.hair)
char.skin = labelled_text("Skin","skin",char.skin)

# ---------- Header ----------
st.title("D&D 3.5 Character Sheet (UI)")
st.caption("Layout-first build. All fields are local session state.")

# ---------- Top Row: Abilities + HP ----------
row_top = st.columns([1,1,1,1,1,1,2.2])
for i, ab in enumerate(["STR","DEX","CON","INT","WIS","CHA"]):
    with row_top[i]:
        total = ability_total(char, ab)
        mod = ability_mod(total)
        st.markdown(f"<div class='card ability-card'><div class='pill-label'>{ab}</div><div class='ability-mod'>{mod:+d}</div><div class='ability-score'>{total}</div></div>", unsafe_allow_html=True)

with row_top[6]:
    # HP card: 3 columns — [Heal/Input/Damage] | [Current/Max + title] | [Temp + Nonlethal]
    st.markdown("**Hit Points**")
    with st.container(border=True):
        st.markdown("<div class='hp-card'>", unsafe_allow_html=True)
        hpcols = st.columns([0.9, 2.4, 0.9])
        # Column 1
        with hpcols[0]:
            st.markdown("<div class='hp-first'>", unsafe_allow_html=True)
            if st.button("Heal", key="btn_heal", use_container_width=True):
                amt = int(st.session_state.get("hp_amount", 0) or 0)
                char.hp_current = min(char.hp_max, char.hp_current + amt)
            st.number_input(" ", key="hp_amount", min_value=0, step=1, label_visibility="collapsed")
            if st.button("Damage", key="btn_damage", use_container_width=True):
                amt = int(st.session_state.get("hp_amount", 0) or 0)
                char.hp_current = max(0, char.hp_current - amt)
            st.markdown("</div>", unsafe_allow_html=True)
        # Column 2
        with hpcols[1]:
            st.markdown(
                f"""
                <div class='hp-mid'>
                  <div>
                    <div class='labels'><span>Current</span><span>Max</span></div>
                    <div style='display:flex;justify-content:center;gap:.4rem;align-items:baseline;'>
                      <span class='big-number'>{char.hp_current}</span>
                      <span class='big-number'>/</span>
                      <span class='big-number'>{char.hp_max}</span>
                    </div>
                  </div>
                  <div class='hp-footer'>Hit Points</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        # Column 3
        with hpcols[2]:
            st.markdown("<div class='hp-side'>", unsafe_allow_html=True)
            char.hp_temp = labelled_number("Temp", "hp_temp", char.hp_temp, min_value=0)
            labelled_number("Nonlethal", "nonlethal", st.session_state.get("nonlethal", 0), min_value=0)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------- Second Row ----------
c1, c2, c3, c4 = st.columns([1.2, 1.0, 1.2, 1.6])
with c1:
    st.markdown("**Saving Throws**")
    with st.container(border=True):
        fort = char.fort_base + ability_mod(ability_total(char, "CON")) + char.save_misc
        ref = char.ref_base + ability_mod(ability_total(char, "DEX")) + char.save_misc
        will = char.will_base + ability_mod(ability_total(char, "WIS")) + char.save_misc
        st.markdown(f"Fortitude: <b>{fort:+d}</b><br/>Reflex: <b>{ref:+d}</b><br/>Will: <b>{will:+d}</b><br/><span class='pill-label'>(base + ability + misc)</span>", unsafe_allow_html=True)

with c2:
    st.markdown("**Initiative**")
    with st.container(border=True):
        ini_total = ability_mod(ability_total(char, "DEX")) + char.initiative_misc
        st.markdown(f"<div class='big-number' style='text-align:center;'>{ini_total:+d}</div>", unsafe_allow_html=True)
    st.markdown("**Speed**")
    with st.container(border=True):
        st.markdown(f"<div class='big-number' style='text-align:center;'>{char.speed}</div><div class='pill-label' style='text-align:center;'>ft.</div>", unsafe_allow_html=True)

with c3:
    st.markdown("**Armor Class**")
    with st.container(border=True):
        dex_mod = ability_mod(ability_total(char, "DEX"))
        ac_total = 10 + char.ac_armor + char.ac_shield + dex_mod + char.ac_natural + char.ac_deflection + char.ac_misc
        touch_ac = 10 + dex_mod + char.ac_deflection + char.ac_misc
        flat_ac = 10 + char.ac_armor + char.ac_shield + char.ac_natural + char.ac_deflection + char.ac_misc
        st.markdown(f"<div class='big-number' style='text-align:center;'>{ac_total}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subgrid'><div class='boxed'>Touch {touch_ac}</div><div class='boxed'>Flat-Footed {flat_ac}</div></div>", unsafe_allow_html=True)
    st.markdown("**Senses**")
    with st.container(border=True):
        senses_text = st.session_state.get("senses_notes", "Add senses (e.g., Darkvision 60 ft.)")
        st.markdown(senses_text)

with c4:
    st.markdown("**Conditions / Defenses**")
    with st.container(border=True):
        cond = st.session_state.get("conditions", "Add Active Conditions")
        defs = st.session_state.get("defenses", "Add Defenses (DR/Resistances)")
        st.markdown(f"<div class='subgrid' style='grid-template-columns:1fr 1fr;'><div class='boxed'>{cond}</div><div class='boxed'>{defs}</div></div>", unsafe_allow_html=True)
    st.markdown("**Base Attack Bonus**")
    with st.container(border=True):
        melee = char.bab + ability_mod(ability_total(char, "STR"))
        ranged = char.bab + ability_mod(ability_total(char, "DEX"))
        grapple = char.bab + ability_mod(ability_total(char, "STR"))
        st.markdown(f"<div class='big-number' style='text-align:center;'>{char.bab:+d}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subgrid'><div class='boxed'>Melee {melee:+d}</div><div class='boxed'>Ranged {ranged:+d}</div><div class='boxed'>Grapple {grapple:+d}</div></div>", unsafe_allow_html=True)

# ---------- Tabs ----------
actions, skills, feats, spells, gear, notes = st.tabs(["Actions","Skills","Feats & Features","Spells","Gear & Wealth","Notes & Export"])

with actions:
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

with skills:
    st.markdown("### Skills — D&D 3.5 list (editable)")
    SKILLS_35 = [
        ("Appraise","INT"),("Balance","DEX"),("Bluff","CHA"),("Climb","STR"),("Concentration","CON"),
        ("Craft (Alchemy)","INT"),("Craft (Armorsmithing)","INT"),("Craft (Weaponsmithing)","INT"),("Craft (Other)","INT"),
        ("Decipher Script","INT"),("Diplomacy","CHA"),("Disable Device","INT"),("Disguise","CHA"),("Escape Artist","DEX"),
        ("Forgery","INT"),("Gather Information","CHA"),("Handle Animal","CHA"),("Heal","WIS"),("Hide","DEX"),
        ("Intimidate","CHA"),("Jump","STR"),("Knowledge (Arcana)","INT"),("Knowledge (Architecture)","INT"),
        ("Knowledge (Dungeoneering)","INT"),("Knowledge (Geography)","INT"),("Knowledge (History)","INT"),
        ("Knowledge (Local)","INT"),("Knowledge (Nature)","INT"),("Knowledge (Nobility)","INT"),
        ("Knowledge (Religion)","INT"),("Knowledge (The Planes)","INT"),("Listen","WIS"),("Move Silently","DEX"),
        ("Open Lock","DEX"),("Perform","CHA"),("Profession","WIS"),("Ride","DEX"),("Search","INT"),
        ("Sense Motive","WIS"),("Sleight of Hand","DEX"),("Speak Language","—"),("Spellcraft","INT"),
        ("Spot","WIS"),("Survival","WIS"),("Swim","STR"),("Tumble","DEX"),("Use Magic Device","CHA"),("Use Rope","DEX")
    ]
    if st.session_state.get("skills_table") is None or st.session_state.get("skills_table_seed") != "3.5":
        st.session_state.skills_table = [{"Skill": s, "Ability": ab, "Ranks": 0, "Misc": 0, "Class": True} for s, ab in SKILLS_35]
        st.session_state.skills_table_seed = "3.5"
    edited = st.data_editor(st.session_state.skills_table, num_rows="dynamic", use_container_width=True, key="skills_editor", column_config={"Class": st.column_config.CheckboxColumn("Class Skill")})
    st.session_state.skills_table = edited

with feats:
    st.markdown("### Feats & Class Features")
    feats_list = taglist("feats_tags", "Feats (type and press Add)")
    features_list = taglist("features_tags", "Class Features")

with spells:
    st.markdown("### Spells")
    st.selectbox("Spell List Level", options=list(range(0,10)), key="spell_level")
    taglist("spells_known", "Known/Prepared Spells")
    st.text_area("Spellbook / Notes", key="spellbook_notes")

with gear:
    st.markdown("### Gear & Wealth")
    taglist("languages", "Languages")
    st.text_area("Weapons & Armor", key="gear_weapons", height=100)
    st.text_area("Equipment & Tools", key="gear_tools", height=120)
    st.number_input("Wealth (gp)", key="wealth_gp", value=0, step=1)

with notes:
    st.markdown("### Notes & Export")
    st.text_area("Background & Personality", key="notes_bg", height=160)
    st.text_area("Allies & Organizations", key="notes_allies", height=120)
    st.text_area("Other Notes", key="notes_other", height=100)

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

    st.download_button("Download Character (JSON)", data=json.dumps(export_dict, indent=2), file_name=f"{char.name or 'character'}.json", mime="application/json")
    st.caption("Use your browser's print dialog on the main page for a quick paper sheet (A4).")
# app.py — D&D 3.5 Character Builder (UI Skeleton, compact HP card)
# Run: streamlit run app.py

import json
from dataclasses import dataclass, asdict
from typing import Dict, List
import streamlit as st

# ---------- Page ----------
st.set_page_config(page_title="D&D 3.5 Character Builder", layout="wide", initial_sidebar_state="expanded")

# ---------- Styles (global + HP compact) ----------
st.markdown(
    """
    <style>
      :root{ --accent:#c62828; --ink:#222; --muted:#666; }
      .small-label { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.15rem; }
      .section { border: 1px solid #e6e6e6; border-radius: 14px; padding: .6rem; margin-bottom: .6rem; background: #fafafa; }
      .card { border: 2px solid var(--accent); border-radius: 12px; padding: .6rem; background: #fff; color:#000; box-shadow: 0 1px 0 rgba(0,0,0,.04) inset; }
      .card * { color:#000; }
      .ability-card { text-align:center; }
      .ability-mod { font-size: 1.4rem; font-weight: 700; line-height: 1; }
      .ability-score { font-size: .8rem; color: var(--muted); }
      .pill-label{ font-size:.75rem; color:#444; text-transform:uppercase; letter-spacing:.06em;}
      .big-number{ font-size:1.8rem; font-weight:700;}
      .subgrid{ display:grid; grid-template-columns: repeat(2,1fr); gap:.4rem; }
      @media print { @page { size: A4; margin: 10mm; } header,[data-testid="baseButton-secondary"]{display:none!important} .card{break-inside:avoid} }

      /* Make Streamlit bordered containers render like white cards */
      div[data-testid="stVerticalBlockBorderWrapper"]{ background:#fff; border:2px solid var(--accent); border-radius:12px; padding:.45rem; }
      div[data-testid="stVerticalBlockBorderWrapper"] *{ color:#000; }

      /* HP Card Compact Styling */
      .hp-card div[data-testid="stVerticalBlockBorderWrapper"] { padding: .2rem !important; }
      .hp-card .hp-first .stButton>button { padding: .1rem .25rem; font-size: .7rem; height: 24px; line-height: 1; }
      .hp-card .hp-first div[data-testid="stNumberInput"] input { height: 24px; font-size: .75rem; padding: 1px 4px; }
      .hp-card .hp-first [data-testid="stVerticalBlock"] { padding-top: .1rem !important; padding-bottom: .1rem !important; margin: 0 !important; }
      .hp-card .hp-mid .labels { justify-content: center; gap: 2rem; font-size: .9rem; letter-spacing:.06em; text-transform:uppercase; color:#333; }
      .hp-card .hp-mid .hp-footer { font-size: 1.1rem; font-weight: 700; text-align: center; margin-top: .1rem; text-transform:uppercase; }
      .hp-card .hp-mid .big-number{ font-size:1.7rem; }
      .hp-card .hp-side input { height: 24px !important; font-size: .75rem !important; padding: 1px 4px !important; }
      .hp-card .hp-side .small-label { font-size: .7rem; margin-bottom: .05rem; }
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
                st.button(f"✕ {t}", key=f"{key}_del_{i}", help="Remove", on_click=lambda t=t: st.session_state[key].remove(t))
    return st.session_state[key]

# ---------- Data Model ----------
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
    str_base: int = 10; dex_base: int = 10; con_base: int = 10
    int_base: int = 10; wis_base: int = 10; cha_base: int = 10
    str_racial: int = 0; dex_racial: int = 0; con_racial: int = 0
    int_racial: int = 0; wis_racial: int = 0; cha_racial: int = 0

    # Combat basics
    hp: int = 0
    hit_die: str = "d10"
    bab: int = 0
    ac_armor: int = 0; ac_shield: int = 0; ac_natural: int = 0; ac_deflection: int = 0; ac_misc: int = 0
    initiative_misc: int = 0
    hp_current: int = 0; hp_max: int = 0; hp_temp: int = 0

    # Saves
    fort_base: int = 0; ref_base: int = 0; will_base: int = 0; save_misc: int = 0

    # Movement
    speed: int = 30

    # Lists (placeholder)
    feats: List[str] = None
    class_features: List[str] = None
    skills: Dict[str, Dict[str, int]] = None
    languages: List[str] = None

if "char" not in st.session_state:
    st.session_state.char = Character()
char: Character = st.session_state.char

# ---------- Sidebar ----------
st.sidebar.header("Character Meta")
char.name = labelled_text("Name", "name", char.name)
char.player = labelled_text("Player", "player", char.player)
char.alignment = labelled_select("Alignment", "alignment", ["LG","NG","CG","LN","N","CN","LE","NE","CE"], index=4)

race_options = ["Human","Elf","Dwarf","Gnome","Halfling","Half-Orc","Half-Elf"]
class_options = ["Barbarian","Bard","Cleric","Druid","Fighter","Monk","Paladin","Ranger","Rogue","Sorcerer","Wizard"]
char.race = labelled_select("Race","race",race_options,index=race_options.index(char.race) if char.race in race_options else 0)
char.character_class = labelled_select("Class","class",class_options,index=class_options.index(char.character_class) if char.character_class in class_options else 4)
char.level = labelled_number("Level","level",max(1,char.level),min_value=1,max_value=20)
char.xp = labelled_number("XP","xp",char.xp,step=100)

st.sidebar.divider()
st.sidebar.subheader("Physical")
char.age = labelled_number("Age","age",char.age,min_value=1)
char.gender = labelled_text("Gender","gender",char.gender)
char.height = labelled_text("Height","height",char.height)
char.weight = labelled_text("Weight","weight",char.weight)
char.eyes = labelled_text("Eyes","eyes",char.eyes)
char.hair = labelled_text("Hair","hair",char.hair)
char.skin = labelled_text("Skin","skin",char.skin)

# ---------- Header ----------
st.title("D&D 3.5 Character Sheet (UI)")
st.caption("Layout-first build. All fields are local session state.")

# ---------- Top Row: Abilities + HP ----------
row_top = st.columns([1,1,1,1,1,1,2.2])
for i, ab in enumerate(["STR","DEX","CON","INT","WIS","CHA"]):
    with row_top[i]:
        total = ability_total(char, ab)
        mod = ability_mod(total)
        st.markdown(f"<div class='card ability-card'><div class='pill-label'>{ab}</div><div class='ability-mod'>{mod:+d}</div><div class='ability-score'>{total}</div></div>", unsafe_allow_html=True)

with row_top[6]:
    # HP card: 3 columns — [Heal/Input/Damage] | [Current/Max + title] | [Temp + Nonlethal]
    st.markdown("**Hit Points**")
    with st.container(border=True):
        st.markdown("<div class='hp-card'>", unsafe_allow_html=True)
        hpcols = st.columns([0.9, 2.4, 0.9])
        # Column 1
        with hpcols[0]:
            st.markdown("<div class='hp-first'>", unsafe_allow_html=True)
            if st.button("Heal", key="btn_heal", use_container_width=True):
                amt = int(st.session_state.get("hp_amount", 0) or 0)
                char.hp_current = min(char.hp_max, char.hp_current + amt)
            st.number_input(" ", key="hp_amount", min_value=0, step=1, label_visibility="collapsed")
            if st.button("Damage", key="btn_damage", use_container_width=True):
                amt = int(st.session_state.get("hp_amount", 0) or 0)
                char.hp_current = max(0, char.hp_current - amt)
            st.markdown("</div>", unsafe_allow_html=True)
        # Column 2
        with hpcols[1]:
            st.markdown(
                f"""
                <div class='hp-mid'>
                  <div>
                    <div class='labels'><span>Current</span><span>Max</span></div>
                    <div style='display:flex;justify-content:center;gap:.4rem;align-items:baseline;'>
                      <span class='big-number'>{char.hp_current}</span>
                      <span class='big-number'>/</span>
                      <span class='big-number'>{char.hp_max}</span>
                    </div>
                  </div>
                  <div class='hp-footer'>Hit Points</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        # Column 3
        with hpcols[2]:
            st.markdown("<div class='hp-side'>", unsafe_allow_html=True)
            char.hp_temp = labelled_number("Temp", "hp_temp", char.hp_temp, min_value=0)
            labelled_number("Nonlethal", "nonlethal", st.session_state.get("nonlethal", 0), min_value=0)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------- Second Row ----------
c1, c2, c3, c4 = st.columns([1.2, 1.0, 1.2, 1.6])
with c1:
    st.markdown("**Saving Throws**")
    with st.container(border=True):
        fort = char.fort_base + ability_mod(ability_total(char, "CON")) + char.save_misc
        ref = char.ref_base + ability_mod(ability_total(char, "DEX")) + char.save_misc
        will = char.will_base + ability_mod(ability_total(char, "WIS")) + char.save_misc
        st.markdown(f"Fortitude: <b>{fort:+d}</b><br/>Reflex: <b>{ref:+d}</b><br/>Will: <b>{will:+d}</b><br/><span class='pill-label'>(base + ability + misc)</span>", unsafe_allow_html=True)

with c2:
    st.markdown("**Initiative**")
    with st.container(border=True):
        ini_total = ability_mod(ability_total(char, "DEX")) + char.initiative_misc
        st.markdown(f"<div class='big-number' style='text-align:center;'>{ini_total:+d}</div>", unsafe_allow_html=True)
    st.markdown("**Speed**")
    with st.container(border=True):
        st.markdown(f"<div class='big-number' style='text-align:center;'>{char.speed}</div><div class='pill-label' style='text-align:center;'>ft.</div>", unsafe_allow_html=True)

with c3:
    st.markdown("**Armor Class**")
    with st.container(border=True):
        dex_mod = ability_mod(ability_total(char, "DEX"))
        ac_total = 10 + char.ac_armor + char.ac_shield + dex_mod + char.ac_natural + char.ac_deflection + char.ac_misc
        touch_ac = 10 + dex_mod + char.ac_deflection + char.ac_misc
        flat_ac = 10 + char.ac_armor + char.ac_shield + char.ac_natural + char.ac_deflection + char.ac_misc
        st.markdown(f"<div class='big-number' style='text-align:center;'>{ac_total}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subgrid'><div class='boxed'>Touch {touch_ac}</div><div class='boxed'>Flat-Footed {flat_ac}</div></div>", unsafe_allow_html=True)
    st.markdown("**Senses**")
    with st.container(border=True):
        senses_text = st.session_state.get("senses_notes", "Add senses (e.g., Darkvision 60 ft.)")
        st.markdown(senses_text)

with c4:
    st.markdown("**Conditions / Defenses**")
    with st.container(border=True):
        cond = st.session_state.get("conditions", "Add Active Conditions")
        defs = st.session_state.get("defenses", "Add Defenses (DR/Resistances)")
        st.markdown(f"<div class='subgrid' style='grid-template-columns:1fr 1fr;'><div class='boxed'>{cond}</div><div class='boxed'>{defs}</div></div>", unsafe_allow_html=True)
    st.markdown("**Base Attack Bonus**")
    with st.container(border=True):
        melee = char.bab + ability_mod(ability_total(char, "STR"))
        ranged = char.bab + ability_mod(ability_total(char, "DEX"))
        grapple = char.bab + ability_mod(ability_total(char, "STR"))
        st.markdown(f"<div class='big-number' style='text-align:center;'>{char.bab:+d}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subgrid'><div class='boxed'>Melee {melee:+d}</div><div class='boxed'>Ranged {ranged:+d}</div><div class='boxed'>Grapple {grapple:+d}</div></div>", unsafe_allow_html=True)

# ---------- Tabs ----------
actions, skills, feats, spells, gear, notes = st.tabs(["Actions","Skills","Feats & Features","Spells","Gear & Wealth","Notes & Export"])

with actions:
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

with skills:
    st.markdown("### Skills — D&D 3.5 list (editable)")
    SKILLS_35 = [
        ("Appraise","INT"),("Balance","DEX"),("Bluff","CHA"),("Climb","STR"),("Concentration","CON"),
        ("Craft (Alchemy)","INT"),("Craft (Armorsmithing)","INT"),("Craft (Weaponsmithing)","INT"),("Craft (Other)","INT"),
        ("Decipher Script","INT"),("Diplomacy","CHA"),("Disable Device","INT"),("Disguise","CHA"),("Escape Artist","DEX"),
        ("Forgery","INT"),("Gather Information","CHA"),("Handle Animal","CHA"),("Heal","WIS"),("Hide","DEX"),
        ("Intimidate","CHA"),("Jump","STR"),("Knowledge (Arcana)","INT"),("Knowledge (Architecture)","INT"),
        ("Knowledge (Dungeoneering)","INT"),("Knowledge (Geography)","INT"),("Knowledge (History)","INT"),
        ("Knowledge (Local)","INT"),("Knowledge (Nature)","INT"),("Knowledge (Nobility)","INT"),
        ("Knowledge (Religion)","INT"),("Knowledge (The Planes)","INT"),("Listen","WIS"),("Move Silently","DEX"),
        ("Open Lock","DEX"),("Perform","CHA"),("Profession","WIS"),("Ride","DEX"),("Search","INT"),
        ("Sense Motive","WIS"),("Sleight of Hand","DEX"),("Speak Language","—"),("Spellcraft","INT"),
        ("Spot","WIS"),("Survival","WIS"),("Swim","STR"),("Tumble","DEX"),("Use Magic Device","CHA"),("Use Rope","DEX")
    ]
    if st.session_state.get("skills_table") is None or st.session_state.get("skills_table_seed") != "3.5":
        st.session_state.skills_table = [{"Skill": s, "Ability": ab, "Ranks": 0, "Misc": 0, "Class": True} for s, ab in SKILLS_35]
        st.session_state.skills_table_seed = "3.5"
    edited = st.data_editor(st.session_state.skills_table, num_rows="dynamic", use_container_width=True, key="skills_editor", column_config={"Class": st.column_config.CheckboxColumn("Class Skill")})
    st.session_state.skills_table = edited

with feats:
    st.markdown("### Feats & Class Features")
    feats_list = taglist("feats_tags", "Feats (type and press Add)")
    features_list = taglist("features_tags", "Class Features")

with spells:
    st.markdown("### Spells")
    st.selectbox("Spell List Level", options=list(range(0,10)), key="spell_level")
    taglist("spells_known", "Known/Prepared Spells")
    st.text_area("Spellbook / Notes", key="spellbook_notes")

with gear:
    st.markdown("### Gear & Wealth")
    taglist("languages", "Languages")
    st.text_area("Weapons & Armor", key="gear_weapons", height=100)
    st.text_area("Equipment & Tools", key="gear_tools", height=120)
    st.number_input("Wealth (gp)", key="wealth_gp", value=0, step=1)

with notes:
    st.markdown("### Notes & Export")
    st.text_area("Background & Personality", key="notes_bg", height=160)
    st.text_area("Allies & Organizations", key="notes_allies", height=120)
    st.text_area("Other Notes", key="notes_other", height=100)

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

    st.download_button("Download Character (JSON)", data=json.dumps(export_dict, indent=2), file_name=f"{char.name or 'character'}.json", mime="application/json")
    st.caption("Use your browser's print dialog on the main page for a quick paper sheet (A4).")
