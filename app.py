import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Handbollsturnering", page_icon="🤾", layout="centered")

# VÄLJ DITT LÖSENORD HÄR
ADMIN_PASSWORD = "handboll123"

# Alla 28 lag
TEAMS = [
    "Skuru IK", "Skogås HK", "Årsta AIK HF", "Spånga HK", "Lidingö HK",
    "Huddinge HK", "Täby HK 2", "Uppsala HK", "AIK", "Kista SC KFUM",
    "IK Bolton", "Åkersberga HK", "Rimbo HK Roslagen", "Sollentuna HK 2",
    "Vallentuna HK", "Skå IK Gul", "Vassunda IF", "Tyresö Handboll",
    "IFK Tumba HK", "Gustavsberg IF HK", "Sannadals SK", "Hammarby IF HF",
    "Skå IK Grön", "Skånela IF", "Täby HBK", "Skuru IK 2",
    "IF Swithiod", "Sollentuna HK"
]

DATA_FILE = "handbollsdata.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {f"Omgång {i}": {} for i in range(1, 5)}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

st.title("🤾 Totaltabell - Östbollen")

# Flikar
tab1, tab2 = st.tabs(["📊 Totaltabell", "🔒 Registrera resultat (Låst)"])

# FLIK 1: BARA LÄSA (Synlig för alla, inklusive din son)
with tab1:
    st.caption("Kriterier: 1. Poäng | 2. Målskillnad | 3. Gjorda mål")
    
    totals = {team: {"S": 0, "V": 0, "O": 0, "F": 0, "GM": 0, "IM": 0} for team in TEAMS}
    for r_data in data.values():
        for t, stats in r_data.items():
            if t in totals:
                for k in ["S", "V", "O", "F", "GM", "IM"]:
                    totals[t][k] += stats.get(k, 0)

    rows = []
    for team, stats in totals.items():
        ms = stats["GM"] - stats["IM"]
        pts = (stats["V"] * 2) + (stats["O"] * 1)
        rows.append({
            "Lag": team,
            "S": stats["S"],
            "V": stats["V"],
            "O": stats["O"],
            "F": stats["F"],
            "GM": stats["GM"],
            "IM": stats["IM"],
            "MS": ms,
            "P": pts
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["P", "MS", "GM"], ascending=[False, False, False]).reset_index(drop=True)
    df.index += 1

    st.dataframe(df, use_container_width=True)

# FLIK 2: KRÄVER LÖSENORD FÖR ATT REDIGERA
with tab2:
    st.header("Registrera resultat")
    
    pwd_input = st.text_input("Ange lösenord för att låsa upp redigering:", type="password")

    if pwd_input == ADMIN_PASSWORD:
        st.success("Lösenord godkänt! Du kan nu spara resultat.")
        
        selected_round = st.selectbox("Välj omgång", [f"Omgång {i}" for i in range(1, 5)])
        selected_team = st.selectbox("Välj lag", TEAMS)

        current_stats = data.get(selected_round, {}).get(selected_team, {"S": 0, "V": 0, "O": 0, "F": 0, "GM": 0, "IM": 0})

        col1, col2 = st.columns(2)
        with col1:
            s = st.number_input("Spelade (S)", min_value=0, value=current_stats["S"])
            v = st.number_input("Vunna (V)", min_value=0, value=current_stats["V"])
            o = st.number_input("Oavgjorda (O)", min_value=0, value=current_stats["O"])
        with col2:
            f = st.number_input("Förlorade (F)", min_value=0, value=current_stats["F"])
            gm = st.number_input("Gjorda mål (GM)", min_value=0, value=current_stats["GM"])
            im = st.number_input("Insläppta mål (IM)", min_value=0, value=current_stats["IM"])

        if st.button("💾 Spara resultat", type="primary"):
            if selected_round not in data:
                data[selected_round] = {}
            data[selected_round][selected_team] = {
                "S": s, "V": v, "O": o, "F": f, "GM": gm, "IM": im
            }
            save_data(data)
            st.success(f"Resultat sparades för {selected_team} i {selected_round}!")
            st.rerun()
    elif pwd_input != "":
        st.error("Fel lösenord.")
    else:
        st.info("Endast behöriga kan registrera matcher. Skriv in lösenordet ovan.")
