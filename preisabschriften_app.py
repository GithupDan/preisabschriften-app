# app.py
import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

# App-Layout
st.set_page_config(page_title="Merchify", layout="wide")

# Logo laden
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("🚨 Logo konnte nicht geladen werden.")

st.sidebar.title("Merchify App")
st.sidebar.markdown("**Price Optimization Made Simple**")

st.title(":bar_chart: Merchify - Preis- & Lageranalyse")

# Tabs
tab1, tab2 = st.tabs(["📦 IST-Daten analysieren", "📝 Plandaten pflegen"])

# --- Tab 1: IST-Daten ---
with tab1:
    st.header(":inbox_tray: IST-Daten hochladen")
    uploaded_file = st.file_uploader("Bitte eine Excel-Datei hochladen", type=["xlsx"])

    if uploaded_file:
        try:
            df_ist = pd.read_excel(uploaded_file, sheet_name='Artikeldaten')
            st.success("IST-Daten erfolgreich geladen!")

            # Vorschau
            st.subheader(":clipboard: Vorschau der Daten")
            st.dataframe(df_ist.head())

            # Filter & Auswahl
            warengruppen = df_ist["Warengruppe"].unique()
            auswahl = st.multiselect("Warengruppen auswählen:", warengruppen, default=list(warengruppen))
            df_filtered = df_ist[df_ist["Warengruppe"].isin(auswahl)]

            # Reichweitenberechnung
            reichweite_df = (
                df_filtered
                .groupby(["Warengruppe", "Preisstufe"])
                .agg({
                    "Lagerbestand": "sum",
                    "Absatz": "sum"
                })
                .reset_index()
            )
            reichweite_df["Reichweite"] = reichweite_df["Lagerbestand"] / reichweite_df["Absatz"].replace(0, pd.NA)

            st.subheader("🧮 Berechnete Reichweite je Warengruppe & Preisstufe")
            st.dataframe(reichweite_df)

            st.subheader("📊 Visualisierung der Reichweiten")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(
                data=reichweite_df,
                x="Warengruppe",
                y="Reichweite",
                hue="Preisstufe",
                palette="viridis",
                ax=ax
            )
            plt.xticks(rotation=45)
            plt.title("Durchschnittliche Reichweite")
            plt.ylabel("Reichweite (Lager/Absatz)")
            plt.xlabel("Warengruppe")
            st.pyplot(fig)

            # Drilldown
            st.subheader(":mag_right: Drilldown für ausgewählte Warengruppe")
            gruppe = st.selectbox("Bitte Warengruppe auswählen", auswahl)
            df_drill = df_filtered[df_filtered["Warengruppe"] == gruppe]
            st.dataframe(df_drill)

        except Exception as e:
            st.error(f"Fehler beim Laden der Datei: {e}")
    else:
        st.info("Bitte lade eine Excel-Datei mit dem Tabellenblatt 'Artikeldaten' hoch.")

# --- Tab 2: Plandaten pflegen ---
with tab2:
    st.header("Plandaten (Excel Register 'Plandaten')")
    uploaded_plan = st.file_uploader("Plandaten hochladen", type="xlsx", key="plan")

    if uploaded_plan:
        try:
            df_plan = pd.read_excel(uploaded_plan, sheet_name='Plandaten')
            st.success("Plandaten erfolgreich geladen!")
            st.dataframe(df_plan)
        except Exception as e:
            st.error(f"Fehler beim Laden der Plandaten: {e}")
    else:
        st.info("Bitte lade eine Excel-Datei mit dem Tabellenblatt 'Plandaten' hoch.")
