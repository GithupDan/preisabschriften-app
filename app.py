
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Seitenlayout und Logo
st.set_page_config(page_title="Merchify", layout="wide")

# Logo einbinden
logo_path = Path(__file__).parent / "logo.png"
with st.sidebar:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.write("🧾 MERCHIFY")
        st.caption("Price Optimization Made Simple")

    st.markdown("---")
    st.header("Navigation")
    selection = st.radio("Gehe zu:", ["📥 IST-Daten", "📊 Analyse & Empfehlung", "🗓️ Planung verwalten"])

# Beispielinhalte für jede Seite
if selection == "📥 IST-Daten":
    st.header("📥 IST-Daten hochladen")
    uploaded_file = st.file_uploader("Lade deine CSV-Datei hoch", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("Datei erfolgreich geladen.")
        st.dataframe(df)

elif selection == "📊 Analyse & Empfehlung":
    st.header("📊 Analyse & Empfehlung")
    st.write("Hier könnten Visualisierungen und Empfehlungen basierend auf den IST-Daten stehen.")

elif selection == "🗓️ Planung verwalten":
    st.header("🗓️ Planung verwalten")
    st.write("Hier kannst du Planwerte eingeben und verwalten.")

# Fußzeile
st.markdown("---")
st.caption("© 2025 Merchify – Price Optimization Made Simple")
