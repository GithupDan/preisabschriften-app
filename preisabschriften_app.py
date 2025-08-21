
import streamlit as st
from PIL import Image

# --- Layout / Branding ---
st.set_page_config(page_title="Merchify", layout="wide")

# Logo laden
logo_path = "bfce79af-9f29-4598-ab84-fc6ce6dd6a11.png"
st.sidebar.image(logo_path, use_column_width=True)
st.sidebar.markdown("## Merchify")
st.sidebar.markdown("*Price Optimization Made Simple*")

# --- Navigation ---
tabs = ["📊 IST-Daten", "📅 Planung verwalten", "📈 Analyse & Empfehlung"]
selected_tab = st.sidebar.radio("Navigation", tabs)

# --- Seiteninhalte ---
if selected_tab == "📊 IST-Daten":
    st.header("📊 IST-Daten hochladen")
    st.info("Hier kannst du IST-Daten im CSV-Format hochladen.")
    uploaded_file = st.file_uploader("CSV-Datei auswählen", type=["csv"])
    if uploaded_file:
        st.success("Datei erfolgreich hochgeladen.")

elif selected_tab == "📅 Planung verwalten":
    st.header("📅 Planung verwalten")
    st.warning("Hier kannst du Planwerte anpassen. (Funktion folgt.)")

elif selected_tab == "📈 Analyse & Empfehlung":
    st.header("📈 Analyse & Drilldown")
    st.info("Hier siehst du Heatmaps, Cluster & Handlungsempfehlungen. (Funktion folgt.)")
