import json
import os
import shutil
import streamlit as st
import pandas as pd

# ============================================================
# INSTÄLLNINGAR & CSS (VÄNSTERSTÄLLNING)
# ============================================================

st.set_page_config(page_title="Handbollsturnering", layout="wide")

# CSS för att vänsterställa all text, tabeller och fält
st.markdown("""
    <style>
    /* Vänsterställ all text och tabeller */
    .stApp, div, p, span, h1, h2, h3, h4, th, td {
        text-align: left !important;
    }
    
    /* Vänsterställ siffror och text i tabeller */
    table {
        text-align: left !important;
        width: 100%;
    }
    th, td {
        text-align: left !important;
        padding: 8px !important;
    }
    
    /* Anpassning för nummer-input */
    input {
        text-align: left !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# FILER & KONSTANTER
# ============================================================

FILNAMN = "handbollstabell.json"
BACKUP_FIL = "handbollstabell_backup.json"
PASSWORD = "tumbahkp13"

TEAMS = [
    "Skuru IK", "Skogås HK", "Årsta AIK HF", "Spånga HK", "Lidingö HK",
    "Huddinge HK", "Täby HK 2", "Uppsala HK", "AIK", "Kista SC KFUM",
    "IK Bolton", "Åkersberga HK", "Rimbo HK Roslagen", "Sollentuna HK 2",
    "Vallentuna HK", "Skå IK Gul", "Vassunda IF", "Tyresö Handboll",
    "IFK Tumba HK", "Gustavsberg IF HK", "Sannadals SK", "Hammarby IF HF",
    "Skå IK Grön", "Skånela IF", "Täby HBK", "Skuru IK 2",
    "IF Swithiod", "Sollentuna HK"
]

FIELDS = ["Sp", "V", "O", "F", "Poäng", "Gjorda mål", "Insläppta mål"]

# ============================================================
# DATAHANTERING
# ============================================================

def create_empty_data():
    result = {}
    for omgang in range(1, 5):
        result[str(omgang)] = {}
        for team in TEAMS:
            result[str(omgang)][team] = {field: 0 for field in FIELDS}
    return result

def load_data():
    if not os.path.exists(FILNAMN):
        return create_empty_data()
    try:
        with open(FILNAMN, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Säkerställ att alla omgångar och lag finns i strukturen
            empty = create_empty_data()
            for r in range(1, 5):
                r_str = str(r)
                if r_str in data:
                    for team in TEAMS:
                        if team in data[r_str]:
                            for field in FIELDS:
                                if field in data[r_str][team]:
                                    empty[r_str][team][field] = int(data[r_str][team][field])
            return empty
    except Exception:
        return create_empty_data()

def save_data(data):
    try:
        if os.path.exists(FILNAMN):
            shutil.copy2(FILNAMN, BACKUP_FIL)
        with open(FILNAMN, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

# Läs in data till session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ============================================================
# TOTALTABELL
# ============================================================

def make_total_table(round_number):
    totals = {team: {field: 0 for field in FIELDS} for team in TEAMS}
    
    for r in range(1, round_number + 1):
        r_str = str(r)
        for team in TEAMS:
            for field in FIELDS:
                totals[team][field] += st.session_state.data[r_str][team][field]
                
    rows = []
    for team in TEAMS:
        made = totals[team]["Gjorda mål"]
        conceded = totals[team]["Insläppta mål"]
        difference = made - conceded
        
        rows.append({
            "Lag": team,
            "Sp": totals[team]["Sp"],
            "V": totals[team]["V"],
            "O": totals[team]["O"],
            "F": totals[team]["F"],
            "Poäng": totals[team]["Poäng"],
            "Gjorda mål": made,
            "Insläppta mål": conceded,
            "Målskillnad": difference
        })
        
    # Sortering: Poäng > Målskillnad > Gjorda mål
    rows.sort(key=lambda x: (x["Poäng"], x["Målskillnad"], x["Gjorda mål"]), reverse=True)
    return rows

# ============================================================
# GRÄNSSNITT & FLIKAR
# ============================================================

st.title("Handbollsturnering")

tab1, tab2 = st.tabs(["Totaltabell", "Inmatning"])

# ------------------------------------------------------------
# FLIK 1: TOTALTABELL
# ------------------------------------------------------------
with tab1:
    st.header("Totaltabell")
    
    selected_round = st.selectbox("Visa tabell efter omgång:", options=[1, 2, 3, 4], index=3)
    
    table_data = make_total_table(selected_round)
    df = pd.DataFrame(table_data)
    df.index = df.index + 1  # Placering från 1
    
    # Visa tabell i Streamlit (vänsterställd via HTML/CSS)
    st.write(df.to_html(classes="table table-striped", justify="left"), unsafe_allow_html=True)

# ------------------------------------------------------------
# FLIK 2: INMATNING (LÖSENORDSSKYDDAD)
# ------------------------------------------------------------
with tab2:
    st.header("Resultatinmatning")
    
    if not st.session_state.authenticated:
        password_input = st.text_input("Mata in lösenord för att redigera:", type="password")
        if st.button("Lås upp"):
            if password_input == PASSWORD:
                st.session_state.authenticated = True
                st.success("Lösenord godkänt!")
                st.rerun()
            else:
                st.error("Felaktigt lösenord.")
    else:
        st.success("Inloggad. Du kan nu ändra statistik.")
        
        omgang = st.selectbox("Välj omgång:", options=[1, 2, 3, 4], key="inmatning_omgang")
        omgang_str = str(omgang)
        
        selected_team = st.selectbox("Välj lag:", options=TEAMS)
        
        st.subheader(f"Statistik för {selected_team} (Omgång {omgang})")
        
        current_values = st.session_state.data[omgang_str][selected_team]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sp = st.number_input("Spelade matcher (Sp)", min_value=0, value=current_values["Sp"])
            v = st.number_input("Vinster (V)", min_value=0, value=current_values["V"])
            o = st.number_input("Oavgjorda (O)", min_value=0, value=current_values["O"])
            f = st.number_input("Förluster (F)", min_value=0, value=current_values["F"])
        with col2:
            poang = st.number_input("Poäng", min_value=0, value=current_values["Poäng"])
            gjorda = st.number_input("Gjorda mål", min_value=0, value=current_values["Gjorda mål"])
            inslappta = st.number_input("Insläppta mål", min_value=0, value=current_values["Insläppta mål"])
            
        if st.button("Spara ändringar"):
            # Validering
            if sp != (v + o + f):
                st.error(f"Fel: Spelade matcher (Sp = {sp}) måste vara lika med summan av V + O + F ({v + o + f}).")
            else:
                st.session_state.data[omgang_str][selected_team] = {
                    "Sp": int(sp),
                    "V": int(v),
                    "O": int(o),
                    "F": int(f),
                    "Poäng": int(poang),
                    "Gjorda mål": int(gjorda),
                    "Insläppta mål": int(inslappta)
                }
                
                if save_data(st.session_state.data):
                    st.success(f"Data sparad för {selected_team} i omgång {omgang}!")
                else:
                    st.error("Kunde inte spara data till fil.")
                    
        if st.button("Logga ut"):
            st.session_state.authenticated = False
            st.rerun()