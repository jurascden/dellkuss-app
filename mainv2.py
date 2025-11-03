import streamlit as st
from datetime import datetime, date
import os
from pathlib import Path
import base64


# ==============================
# APP KONFIGURATION
# ==============================
st.set_page_config(
    page_title="DellKuss Rechnungsmanager",
    page_icon="💼",
    layout="wide"
)

# ==============================
# STYLING
# ==============================
st.markdown("""
<style>
/* === Grundlayout === */
.stApp {
    background-color: #FFFFFF;
    color: #111111;
    font-family: 'Inter', sans-serif;
}

/* === Sidebar dunkel, Text weiß === */
[data-testid="stSidebar"] {
    background-color: #0F1116 !important;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* === Buttons === */
.stButton>button {
    background-color: #00635A !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: none !important;
    transition: 0.3s !important;
}
.stButton>button:hover {
    background-color: #8B5CF6 !important;
}

/* === Labels & Eingabetexte schwarz === */
label,
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* === Eingabefelder (Text, Zahl, Select) === */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"],
textarea {
    color: #000000 !important;
    background-color: #FFFFFF !important;
    border: 1px solid #00635A !important;
    border-radius: 6px !important;
}

/* === Farbe und Stil der st.metric Werte === */
div[data-testid="stMetricValue"] {
    color: #1F8A70 !important;     /* hier deine gewünschte Farbe */
    font-weight: 800 !important;   /* fett für bessere Lesbarkeit */
}
div[data-testid="stMetricLabel"] {
    color: #000000 !important;     /* Label (z. B. "Summe netto") in schwarz */
    font-weight: 600 !important;
}          
</style>
""", unsafe_allow_html=True)

# ==============================
# LOGO ANZEIGE
# ==============================
def get_base64_logo(logo_path):
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_path = Path("assets/logo.png")
logo_base64 = get_base64_logo(logo_path)
if logo_base64:
    st.markdown(
        f"""<div style="display:flex; justify-content:center; margin-bottom:1.5rem;">
            <img src="data:image/png;base64,{logo_base64}" width="220">
        </div>""",
        unsafe_allow_html=True
    )

# ==============================
# NAVIGATION
# ==============================
page = st.sidebar.radio("Navigation", ["🏠 Startseite", "🧾 Rechnung erstellen", "📚 Archiv"])

# ==============================
# STARTSEITE
# ==============================
if page == "🏠 Startseite":
    st.write("Willkommen im **DellKuss Rechnungsmanager**. Wählen Sie eine Funktion im Menü.")

# ==============================
# RECHNUNG ERSTELLEN
# ==============================
elif page == "🧾 Rechnung erstellen":
    st.header("🧾 Neue Rechnung")

    # --- Kundendaten ---
    st.subheader("👤 Kundendaten")
    col1, col2 = st.columns(2)
    with col1:
        kunde_anrede = st.selectbox("Anrede", ["Herr", "Frau", "Firma"])
        kunde_name = st.text_input("Name / Firma")
        kunde_adresse = st.text_input("Straße und Hausnummer")
    with col2:
        kunde_ort = st.text_input("PLZ / Ort")
        kunde_tel = st.text_input("Telefonnummer")


    # --- Fahrzeugdaten ---
    st.subheader("🚗 Fahrzeugdaten")
    col1, col2 = st.columns(2)
    with col1:
        fahrzeug_marke = st.text_input("Marke / Typ")
        fahrzeug_farbe = st.text_input("Farbe")
    with col2:
        fahrzeug_baujahr = st.text_input("Baujahr")
        fahrzeug_fin = st.text_input("Fahrgestellnummer (FIN)")

    # --- Leistungspositionen ---
    st.subheader("💼 Leistungspositionen")
    rechnungsnr_index = st.text_input("Rechnungsnr_Index")
    rechnungsdatum = st.date_input("Rechnungsdatum", value=date.today()).strftime("%d.%m.%Y")
    rechnungsnummer_datum = rechnungsdatum
    anzahl_positionen = st.number_input("Anzahl der Positionen", min_value=1, max_value=50, value=3)

    col_h1, col_h2 = st.columns([4, 1])
    with col_h1: st.markdown("**Beschreibung**")
    with col_h2: st.markdown("**Gesamtpreis (€)**")

    positionen = []
    for i in range(int(anzahl_positionen)):
        col1, col2 = st.columns([4, 1])
        with col1:
            beschreibung = st.text_input("Beschreibung", key=f"beschreibung_{i}", label_visibility="collapsed")
        with col2:
            betrag = st.number_input("Gesamt (€)", min_value=0.0, step=1.0, format="%.2f", key=f"betrag_{i}", label_visibility="collapsed")
        positionen.append((beschreibung, betrag))

    # --- Gesamtsummen ---
    st.subheader("🧮 Gesamtsumme")
    summe_netto = sum([betrag for _, betrag in positionen])
    mwst = summe_netto * 0.19
    summe_brutto = summe_netto + mwst

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Summe netto (€)", f"{summe_netto:,.2f}")
    with col2: st.metric("MwSt (19%) (€)", f"{mwst:,.2f}")
    with col3: st.metric("Gesamtbetrag (€)", f"{summe_brutto:,.2f}")

    # --- Aktionen ---
    st.subheader("💾 Aktionen")

    from utils.pdf_generator_v2 import create_invoice_pdf

    if st.button("📄 PDF erstellen"):
        # --- Rechnungsnummer manuell zusammensetzen ---
        rechnungsdatum_key = rechnungsdatum.replace(".", "")  # z.B. 31102025
        rechnungsnummer = f"{rechnungsdatum_key}{rechnungsnr_index}"  # z.B. 311020253400
        # Dateipfad
        pdf_folder = Path("pdf/export")
        pdf_folder.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"Rechnung_{rechnungsnummer}.pdf"
        pdf_path = pdf_folder / pdf_filename

        # Daten vorbereiten für PDF
        kunde = {
            "anrede": kunde_anrede,
            "name": kunde_name,
            "adresse": kunde_adresse,
            "ort": kunde_ort,
        }

        fahrzeug = {
            "marke": fahrzeug_marke,
            "baujahr": fahrzeug_baujahr,
            "farbe": fahrzeug_farbe,
            "fin": fahrzeug_fin,
        }

        positionen_liste = []
        for i in range(int(anzahl_positionen)):
            beschreibung = st.session_state.get(f"beschreibung_{i}", "")
            betrag = st.session_state.get(f"betrag_{i}", 0.0)
            positionen_liste.append({
                "beschreibung": beschreibung,
                "summe": betrag
            })

        # Summen berechnen
        summe_netto = sum([p["summe"] for p in positionen_liste])
        summen = {
            "datum": rechnungsdatum,
            "rechnungsnummer": rechnungsnummer,
            "netto": summe_netto,
            "mwst": summe_netto * 0.19,
            "brutto": summe_netto * 1.19
        }


        # PDF erzeugen
        create_invoice_pdf(
            str(pdf_path),
            str(logo_path),
            kunde,
            fahrzeug,
            positionen_liste,
            summen
        )

        # Download anzeigen
        with open(pdf_path, "rb") as f:
            st.success("✅ Rechnung erfolgreich erstellt!")

# ==============================
# ARCHIV
# ==============================
elif page == "📚 Archiv":
    st.subheader("📚 Rechnungsarchiv")
    st.write("Hier können erstellte Rechnungen angezeigt oder geöffnet werden.")

st.markdown("---")
st.caption("© 2025 DellKuss – Der Dellendoktor | Lokale Rechnungsverwaltung ohne Cloud")
