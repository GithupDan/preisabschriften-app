# app.py
import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Optional: Theme via config.toml falls gewünscht (.streamlit/config.toml)
# [theme]
# primaryColor = "#1c7ed6"
# backgroundColor = "#ffffff"
# secondaryBackgroundColor = "#f8f9fa"
# textColor = "#212529"
# font = "sans serif"

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

# Dateiupload
st.header(":inbox_tray: IST-Daten hochladen")
uploaded_file = st.file_uploader("Bitte eine Excel-Datei hochladen", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Datei erfolgreich geladen!")

    # Basisansicht
    st.subheader(":clipboard: Vorschau der Daten")
    st.dataframe(df.head())

    # Filter & Auswahl
    warengruppen = df["Warengruppe"].unique()
    auswahl = st.multiselect("Warengruppen auswählen:", warengruppen, default=list(warengruppen))
    df_filtered = df[df["Warengruppe"].isin(auswahl)]

    # Heatmap vorbereiten
    st.subheader(":art: Heatmap: Artikelanzahl & Reichweite")
    heatmap_data = df_filtered.groupby(["Warengruppe", "Preisstufe"]).agg(
        Artikelanzahl=("Artikelnummer", "count"),
        Reichweite_Berechnet=("Lagerbestand", "sum") / df_filtered.groupby(["Warengruppe", "Preisstufe"]).agg({"Absatz": "sum"})
    ).reset_index()

    heatmap_data_pivot = heatmap_data.pivot(index="Warengruppe", columns="Preisstufe", values="Reichweite_Berechnet")

    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data_pivot, cmap="YlGnBu", annot=True, fmt=".1f", linewidths=.5)
    plt.title("Reichweite pro Warengruppe & Preisstufe")
    st.pyplot(plt.gcf())

    # Drilldown
    st.subheader(":mag_right: Drilldown für ausgewählte Warengruppe")
    gruppe = st.selectbox("Bitte Warengruppe auswählen", auswahl)
    df_drill = df_filtered[df_filtered["Warengruppe"] == gruppe]
    st.dataframe(df_drill)

else:
    st.info("Bitte lade eine Excel-Datei mit den notwendigen Daten hoch. Erwartete Spalten: Artikelnummer, Warengruppe, Preisstufe, Lagerbestand, Absatz")
