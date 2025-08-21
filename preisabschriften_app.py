
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Preisabschriften Web-App", layout="wide")

# --- Dummy Monatsplanung generieren (wenn keine Datei geladen wird) ---
def load_default_planung():
    months = ["Oktober", "November", "Dezember", "Januar", "Februar", "März",
              "April", "Mai", "Juni", "Juli", "August", "September"]
    warengruppen = ["Hemd Langarm", "T-Shirts", "Polos"]
    plan_rows = []
    for wg in warengruppen:
        for month in months:
            plan_rows.append({
                "Warengruppe": wg,
                "Monat": month,
                "Zielreichweite (Wochen)": 20,
                "Abschrift hoch (%)": 30,
                "Abschrift mittel (%)": 20,
                "Abschrift gering (%)": 10,
                "Reduzierungsläufe / Monat": 2
            })
    return pd.DataFrame(plan_rows)


# App Tabs: IST-Daten | Planung | Analyse & Empfehlung
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 IST-Daten", "📝 Planung verwalten", "📈 Analyse & Empfehlung", "📊 Visualisierung"])

with tab1:
st.header("📊 IST-Daten hochladen")
    uploaded_ist = st.file_uploader("IST-Daten als CSV hochladen", type=["csv"])
    if uploaded_ist:
        df_ist = pd.read_csv(uploaded_ist, sep=";", encoding="utf-8")
        if df_ist.shape[1] == 1:
            df_ist = df_ist.iloc[:,0].str.split(",", expand=True)
            df_ist.columns = df_ist.iloc[0]
            df_ist = df_ist.drop(0).reset_index(drop=True)
        st.success("IST-Daten erfolgreich geladen.")
        st.dataframe(df_ist, use_container_width=True)
        st.session_state["ist_daten"] = df_ist

with tab2:
st.header("📝 Planung verwalten")
    uploaded_plan = st.file_uploader("📤 Eigene Planung hochladen (.xlsx)", type=["xlsx"])
    if uploaded_plan:
        df_plan = pd.read_excel(uploaded_plan)
        st.success("Planung erfolgreich geladen.")
    else:
        df_plan = load_default_planung()

    df_plan_edit = st.data_editor(df_plan, num_rows="dynamic", use_container_width=True)
    st.session_state["plan_daten"] = df_plan_edit

    excel_out = io.BytesIO()
    with pd.ExcelWriter(excel_out, engine="xlsxwriter") as writer:
        df_plan_edit.to_excel(writer, index=False, sheet_name="Planung")
    st.download_button(
        label="📥 Bearbeitete Planung als Excel herunterladen",
        data=excel_out.getvalue(),
        file_name="geplante_monatswerte.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with tab3:
st.header("📈 Analyse & Handlungsempfehlung")

    if "ist_daten" in st.session_state and "plan_daten" in st.session_state:
        df_ist = st.session_state["ist_daten"].copy()
        df_plan = st.session_state["plan_daten"].copy()

        # Formatieren
        df_ist.columns = [str(c).strip() for c in df_ist.columns]
        df_ist["RW"] = pd.to_numeric(df_ist["RW"], errors="coerce")
        df_ist["Warengruppe"] = df_ist["Warengruppe"].str.strip()
        df_ist["Monat"] = pd.to_datetime(df_ist["Datum"], errors="coerce").dt.month_name()

        # Merge IST + PLAN über Warengruppe + Monat
        merged = pd.merge(df_ist, df_plan, on=["Warengruppe", "Monat"], how="left")

        # Empfehlungen berechnen
        def empfehlung(row):
            if pd.isna(row["RW"]) or pd.isna(row["Zielreichweite (Wochen)"]):
                return None
            delta = row["RW"] - row["Zielreichweite (Wochen)"]
            if delta > 8:
                return row["Abschrift hoch (%)"]
            elif delta > 4:
                return row["Abschrift mittel (%)"]
            elif delta > 0:
                return row["Abschrift gering (%)"]
            else:
                return 0

        merged["Empfohlene Abschrift (%)"] = merged.apply(empfehlung, axis=1)

        st.dataframe(merged[["SKU", "Warengruppe", "Monat", "RW", "Zielreichweite (Wochen)", "Empfohlene Abschrift (%)"]], use_container_width=True)

        # Download der Vorschlagsliste
        excel_out = io.BytesIO()
        with pd.ExcelWriter(excel_out, engine="xlsxwriter") as writer:
            merged.to_excel(writer, index=False, sheet_name="Empfehlung")
        st.download_button(
            label="📥 Vorschlagsliste als Excel herunterladen",
            data=excel_out.getvalue(),
            file_name="abschriften_empfehlung.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Bitte lade zuerst IST-Daten und Planwerte in den vorherigen Tabs hoch.")

with tab4:
    import seaborn as sns
    import matplotlib.pyplot as plt
    
st.header("📊 Visualisierung: Artikelstruktur & Analysen")
    
    if "ist_daten" in st.session_state:
        df_vis = st.session_state["ist_daten"].copy()
        df_vis.columns = [str(c).strip() for c in df_vis.columns]
    
        df_vis["Preis"] = pd.to_numeric(df_vis["Preis"], errors="coerce")
        df_vis["Absatz"] = pd.to_numeric(df_vis["Absatz"], errors="coerce")
        df_vis["Lagerbestand"] = pd.to_numeric(df_vis["Lagerbestand"], errors="coerce")
        df_vis["Umsatz"] = df_vis["Preis"] * df_vis["Absatz"]
        df_vis["Warengruppe"] = df_vis["Warengruppe"].str.strip()
        df_vis["KW"] = df_vis["KW"].astype(str)
    
        # Preisstufen
        preis_bins = [0, 20, 30, 40, 50, 60, 100]
        preis_labels = ["<20", "20–30", "30–40", "40–50", "50–60", "60+"]
        df_vis["Preisstufe"] = pd.cut(df_vis["Preis"], bins=preis_bins, labels=preis_labels)
    
        # Pivot: Artikelanzahl
        pivot_count = df_vis.pivot_table(index="Warengruppe", columns="Preisstufe", values="SKU", aggfunc="count", fill_value=0)
    
        # Pivot: Reichweite = Lager / Absatz
        pivot_lager = df_vis.pivot_table(index="Warengruppe", columns="Preisstufe", values="Lagerbestand", aggfunc="sum", fill_value=0)
        pivot_absatz = df_vis.pivot_table(index="Warengruppe", columns="Preisstufe", values="Absatz", aggfunc="sum", fill_value=0)
        pivot_rw_custom = pivot_lager / pivot_absatz.replace(0, np.nan)
        pivot_rw_custom = pivot_rw_custom.replace([np.inf, -np.inf], np.nan).fillna(0)
    
        sns.set(style="whitegrid")
    
        # 🔢 Artikelanzahl Heatmap
        st.subheader("🔢 Artikelanzahl pro Warengruppe & Preisstufe")
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot_count, annot=True, fmt="d", cmap="PuBuGn", cbar=True, ax=ax1)
        ax1.set_xlabel("Preisstufe")
        ax1.set_ylabel("Warengruppe")
        ax1.set_title("Anzahl Artikel je Preisstufe")
        st.pyplot(fig1)
    
        # 📏 Reichweite Heatmap
        st.subheader("📏 Berechnete Reichweite (Lager / Absatz)")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot_rw_custom, annot=True, fmt=".1f", cmap="YlGnBu", cbar=True, ax=ax2)
        ax2.set_xlabel("Preisstufe")
        ax2.set_ylabel("Warengruppe")
        ax2.set_title("Reichweite nach Formel Lager / Absatz")
        st.pyplot(fig2)
    
        # 🎯 Preisverteilung Boxplot
        st.subheader("🎯 Preisverteilung nach Warengruppe")
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        sns.boxplot(x="Warengruppe", y="Preis", data=df_vis, palette="Set3")
        ax3.set_title("Preisspannen je Warengruppe")
        ax3.set_ylabel("Preis (€)")
        st.pyplot(fig3)
    
        # 🔠 ABC-Analyse
        st.subheader("🔠 ABC-Analyse basierend auf Umsatz")
        df_abc = df_vis[["SKU", "Umsatz"]].groupby("SKU").sum().sort_values("Umsatz", ascending=False)
        df_abc["Umsatzanteil"] = df_abc["Umsatz"] / df_abc["Umsatz"].sum()
        df_abc["kumuliert"] = df_abc["Umsatzanteil"].cumsum()
        df_abc["ABC"] = pd.cut(df_abc["kumuliert"], bins=[0, 0.2, 0.5, 1], labels=["A", "B", "C"])
    
        abc_counts = df_abc["ABC"].value_counts().sort_index()
        fig4, ax4 = plt.subplots()
        sns.barplot(x=abc_counts.index, y=abc_counts.values, palette=["#76b900", "#f0ad4e", "#d9534f"], ax=ax4)
        ax4.set_title("ABC-Verteilung nach SKU (Umsatzbasiert)")
        ax4.set_xlabel("Kategorie")
        ax4.set_ylabel("Anzahl SKUs")
        st.pyplot(fig4)
    
        # 📈 Zeitverlauf Absatz & Lagerbestand
        st.subheader("📈 Zeitverlauf Absatz & Lagerbestand je Kalenderwoche")
        trend_df = df_vis.groupby("KW")[["Absatz", "Lagerbestand"]].sum().reset_index()
        fig5, ax5 = plt.subplots()
        trend_df.set_index("KW")[["Absatz", "Lagerbestand"]].plot(ax=ax5, marker="o", linewidth=2)
        ax5.set_title("Entwicklung über Kalenderwochen")
        ax5.set_ylabel("Einheiten")
        ax5.grid(True)
        st.pyplot(fig5)
    
    else:
        st.info("Bitte lade zuerst die IST-Daten im Tab '📊 IST-Daten' hoch.")

with tab5:
    import seaborn as sns
    import matplotlib.pyplot as plt

st.set_page_config(
    layout="wide",
    page_title="Merchify – Preisabschriften",
    page_icon="📉"
)

st.markdown("""
    <style>
        .stApp { background-color: #f9f9fb; }
        .stTabs [role="tab"] {
            background-color: #ffffff;
            color: #333;
            padding: 10px;
            margin-right: 4px;
            border: 1px solid #e0e0e0;
            border-radius: 8px 8px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #007acc !important;
            color: white !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.image("logo_merchify.png", width=220)
st.title("Merchify – Dynamische Preisabschriften")
st.markdown("🧠 *Smart Markdown Decisions. Real-Time. Retail Ready.*")
st.markdown("---")

st.set_page_config(
    layout="wide",
    page_title="Merchify – Preisabschriften",
    page_icon="📉"
)

st.markdown("""
    <style>
        body {
            font-family: "Segoe UI", sans-serif;
            background-color: #f9f9fb;
        }
        .stApp {
            background-color: #f9f9fb;
        }
        .stTabs [role="tab"] {
            background-color: #ffffff;
            color: #333;
            padding: 10px;
            margin-right: 4px;
            border: 1px solid #e0e0e0;
            border-radius: 8px 8px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #007acc !important;
            color: white !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/merchify-assets/logo/main/logo_text.png", width=200)
st.title("Merchify – Dynamische Preisabschriften")
st.markdown("📊 Intelligente Steuerung deiner Preisaktionen mit Lager-, Absatz- & Reichweitendaten")
st.markdown("---")
    
st.header("📊 Visualisierung & Drilldown")
    
    if "ist_daten" in st.session_state:
        df_vis = st.session_state["ist_daten"].copy()
        df_vis.columns = [str(c).strip() for c in df_vis.columns]
    
        df_vis["Preis"] = pd.to_numeric(df_vis["Preis"], errors="coerce")
        df_vis["Absatz"] = pd.to_numeric(df_vis["Absatz"], errors="coerce")
        df_vis["Lagerbestand"] = pd.to_numeric(df_vis["Lagerbestand"], errors="coerce")
        df_vis["Umsatz"] = df_vis["Preis"] * df_vis["Absatz"]
        df_vis["Warengruppe"] = df_vis["Warengruppe"].str.strip()
        df_vis["KW"] = df_vis["KW"].astype(str)
    
        preis_bins = [0, 20, 30, 40, 50, 60, 100]
        preis_labels = ["<20", "20–30", "30–40", "40–50", "50–60", "60+"]
        df_vis["Preisstufe"] = pd.cut(df_vis["Preis"], bins=preis_bins, labels=preis_labels)
    
        # Drilldown Auswahl
        warengruppen = df_vis["Warengruppe"].dropna().unique().tolist()
        selected_wg = st.selectbox("🔎 Wähle eine Warengruppe für Detailanalysen", warengruppen)
    
        df_wg = df_vis[df_vis["Warengruppe"] == selected_wg]
    
        # Heatmap Artikelanzahl (gefiltert)
        pivot_count = df_wg.pivot_table(index="Warengruppe", columns="Preisstufe", values="SKU", aggfunc="count", fill_value=0)
        st.subheader("🔢 Artikelanzahl pro Preisstufe")
        fig1, ax1 = plt.subplots(figsize=(8, 2))
        sns.heatmap(pivot_count, annot=True, fmt="d", cmap="PuBuGn", cbar=True, ax=ax1)
        ax1.set_title(f"Artikelanzahl ({selected_wg})")
        st.pyplot(fig1)
    
        # Reichweite (Lager / Absatz)
        pivot_lager = df_wg.pivot_table(index="Warengruppe", columns="Preisstufe", values="Lagerbestand", aggfunc="sum", fill_value=0)
        pivot_absatz = df_wg.pivot_table(index="Warengruppe", columns="Preisstufe", values="Absatz", aggfunc="sum", fill_value=0)
        pivot_rw_custom = pivot_lager / pivot_absatz.replace(0, np.nan)
        pivot_rw_custom = pivot_rw_custom.replace([np.inf, -np.inf], np.nan).fillna(0)
    
        st.subheader("📏 Reichweite pro Preisstufe (Lager / Absatz)")
        fig2, ax2 = plt.subplots(figsize=(8, 2))
        sns.heatmap(pivot_rw_custom, annot=True, fmt=".1f", cmap="YlGnBu", cbar=True, ax=ax2)
        ax2.set_title(f"Reichweite ({selected_wg})")
        st.pyplot(fig2)
    
        # Preisverteilung (Boxplot)
        st.subheader("🎯 Preisverteilung dieser Warengruppe")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.boxplot(x="Preis", data=df_wg, color="skyblue", orient="h")
        ax3.set_title(f"Preisspanne ({selected_wg})")
        st.pyplot(fig3)
    
        # ABC-Analyse (nur diese WG)
        st.subheader("🔠 ABC-Analyse (Umsatz)")
        df_abc = df_wg[["SKU", "Umsatz"]].groupby("SKU").sum().sort_values("Umsatz", ascending=False)
        df_abc["Umsatzanteil"] = df_abc["Umsatz"] / df_abc["Umsatz"].sum()
        df_abc["kumuliert"] = df_abc["Umsatzanteil"].cumsum()
        df_abc["ABC"] = pd.cut(df_abc["kumuliert"], bins=[0, 0.2, 0.5, 1], labels=["A", "B", "C"])
        abc_counts = df_abc["ABC"].value_counts().sort_index()
        fig4, ax4 = plt.subplots()
        sns.barplot(x=abc_counts.index, y=abc_counts.values, palette=["#76b900", "#f0ad4e", "#d9534f"], ax=ax4)
        ax4.set_title("ABC-Verteilung (nur diese Warengruppe)")
        ax4.set_xlabel("Kategorie")
        ax4.set_ylabel("Anzahl SKUs")
        st.pyplot(fig4)
    
        # KW-Verlauf (Absatz & Lagerbestand)
        st.subheader("📈 Zeitverlauf: Absatz & Lagerbestand")
        trend_df = df_wg.groupby("KW")[["Absatz", "Lagerbestand"]].sum().reset_index()
        fig5, ax5 = plt.subplots()
        trend_df.set_index("KW")[["Absatz", "Lagerbestand"]].plot(ax=ax5, marker="o", linewidth=2)
        ax5.set_title(f"Kalenderwochen-Verlauf ({selected_wg})")
        ax5.set_ylabel("Einheiten")
        ax5.grid(True)
        st.pyplot(fig5)
    else:
        st.info("Bitte lade zuerst die IST-Daten im Tab '📊 IST-Daten' hoch.")
