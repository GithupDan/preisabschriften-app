import joblib
import os

# Modell laden
model_path = "abschriften_model.pkl"
model = joblib.load(model_path) if os.path.exists(model_path) else None


import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Seiten-Layout definieren
st.set_page_config(
    page_title="Merchify – Preis- & Lageranalyse",
    page_icon="📊",
    layout="wide"
)

# Logo + Titel
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("logo.png", width=70)
with col2:
    st.markdown("## **Merchify – Preis- & Lageranalyse**")
    st.caption("Plan smarter. Reduziere besser.")

# Tabs definieren
tab1, tab2 = st.tabs(["📈 IST-Daten analysieren", "🗓️ Plandaten pflegen"])

# === TAB 1 ===
with tab1:
    st.subheader("🔍 IST-Daten hochladen")
    ist_file = st.file_uploader("Lade eine Excel-Datei mit dem Tabellenblatt **Artikeldaten** hoch.", type="xlsx", key="ist")
    
    if ist_file:
        try:
            df = pd.read_excel(ist_file, sheet_name="Artikeldaten")
            st.success("Datei erfolgreich geladen ✅")
            st.dataframe(df)

            # Gruppierung
            df_filtered = df.dropna(subset=["Warengruppe", "Preisstufe"])
            grouped = df_filtered.groupby(["Warengruppe", "Preisstufe"]).agg({
                "Absatz": "sum",
                "Lagerbestand": "sum"
            }).reset_index()

            grouped["Reichweite_Berechnet"] = grouped["Lagerbestand"] / grouped["Absatz"]

            st.subheader("📊 Reichweitenanalyse")
            st.dataframe(grouped)

            # Visualisierung
            st.subheader("📉 Visualisierung")
            plt.figure(figsize=(10, 5))
            sns.barplot(data=grouped, x="Warengruppe", y="Reichweite_Berechnet", hue="Preisstufe", palette="Blues")
            plt.xticks(rotation=45)
            plt.title("Reichweite nach Warengruppe und Preisstufe")
            st.pyplot(plt.gcf())

        except Exception as e:
            st.error(f"Fehler beim Laden der Datei: {e}")

# === TAB 2 ===
with tab2:
    st.subheader("📥 Plandaten hochladen")
    plan_file = st.file_uploader("Bitte lade eine Excel-Datei mit dem Tabellenblatt **Plandaten** hoch.", type="xlsx", key="plan")

    if plan_file:
        try:
            df_plan = pd.read_excel(plan_file, sheet_name="Plandaten")
            st.success("Plandaten erfolgreich geladen ✅")
            st.dataframe(df_plan)

        except Exception as e:
            st.error(f"Fehler beim Laden der Datei: {e}")
