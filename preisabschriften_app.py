
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
tab1, tab2, tab3, tab4 = st.tabs(["📊 IST-Daten", "📝 Planung verwalten", "📈 Analyse & Empfehlung", "📊 Visualisierung"])

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
    
    st.header("📊 Visualisierung: Artikelstruktur & Reichweiten")
    
    if "ist_daten" in st.session_state:
        df_vis = st.session_state["ist_daten"].copy()
        df_vis.columns = [str(c).strip() for c in df_vis.columns]
    
        # Konvertieren und filtern
        df_vis["Preis"] = pd.to_numeric(df_vis["Preis"], errors="coerce")
        df_vis["RW"] = pd.to_numeric(df_vis["RW"], errors="coerce")
        df_vis["Warengruppe"] = df_vis["Warengruppe"].str.strip()
    
        # Preisstufen definieren
        preis_bins = [0, 20, 30, 40, 50, 60, 100]
        preis_labels = ["<20", "20–30", "30–40", "40–50", "50–60", "60+"]
        df_vis["Preisstufe"] = pd.cut(df_vis["Preis"], bins=preis_bins, labels=preis_labels)
    
        # Pivot-Tabellen erstellen
        pivot_count = df_vis.pivot_table(index="Warengruppe", columns="Preisstufe", values="SKU", aggfunc="count", fill_value=0)
        pivot_rw = df_vis.pivot_table(index="Warengruppe", columns="Preisstufe", values="RW", aggfunc="sum", fill_value=0)
    
        # Stil setzen
        sns.set(style="whitegrid")
    
        # Heatmap 1 – Artikelanzahl
        st.subheader("🔢 Artikelanzahl pro Warengruppe & Preisstufe")
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot_count, annot=True, fmt="d", cmap="PuBuGn", cbar=True, ax=ax1)
        ax1.set_xlabel("Preisstufe")
        ax1.set_ylabel("Warengruppe")
        ax1.set_title("Anzahl Artikel je Preisstufe")
        st.pyplot(fig1)
    
        # Heatmap 2 – Reichweite
        st.subheader("📏 Kumulierte Reichweite pro Warengruppe & Preisstufe")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot_rw, annot=True, fmt=".1f", cmap="YlGnBu", cbar=True, ax=ax2)
        ax2.set_xlabel("Preisstufe")
        ax2.set_ylabel("Warengruppe")
        ax2.set_title("Summierte RW je Preisstufe")
        st.pyplot(fig2)
    else:
        st.info("Bitte lade zuerst die IST-Daten im Tab '📊 IST-Daten' hoch.")
