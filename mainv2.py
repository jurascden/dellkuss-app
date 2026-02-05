import streamlit as st
from datetime import datetime, date
import os
from pathlib import Path
import base64
from io import BytesIO
from utils.storage import save_invoice, get_all_invoices, get_invoice_by_number, delete_invoice
import pandas as pd
import base64

# ==============================
# EDIT MODE STATE
# ==============================
if "is_edit_mode" not in st.session_state:
    st.session_state["is_edit_mode"] = False

if "edit_invoice_number" not in st.session_state:
    st.session_state["edit_invoice_number"] = None

if "edit_loaded_for" not in st.session_state:
    st.session_state["edit_loaded_for"] = None

# ==============================
# APP KONFIGURATION
# ==============================
st.set_page_config(
    page_title="DellKuss Mini-App",
    page_icon="🦞",
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

/* === Button PDF erstellen === */
.stButton>button {
    background-color: #00635A !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: none !important;
    transition: 0.3s !important;
}
.stButton>button:hover {
    background-color: #350c94 !important;
}

/* === Download-Button PDF herunterladen === */
.stDownloadButton > button {
    background-color: #9c3548 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    border: none !important;
    transition: 0.3s !important;
}
.stDownloadButton > button:hover {
    background-color: #350c94 !important;
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
    border: 1px solid #0F1116 !important;
    border-radius: 6px !important;
}

/* === Farbe und Stil der st.metric Werte Summe MwSt Endsumme === */
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
if "seite" not in st.session_state:
    st.session_state["seite"] = "🌤️ Startseite"

# Redirect aus Archiv -> Rechnung erstellen
if st.session_state.get("navigate_to"):
    st.session_state["seite"] = st.session_state.pop("navigate_to")

page = st.sidebar.radio(
    "Navigation",
    ["🌤️ Startseite", "🗃️ Rechnung erstellen", "🐙 Archiv"],
    key="seite"
)

# ==============================
# STARTSEITE
# ==============================
if page == "🌤️ Startseite":
    st.write("Willkommen in der **DellKuss Mini-App**. Links eine Funktion im Menü auswählen.")

# ==============================
# RECHNUNG ERSTELLEN
# ==============================
elif page == "🗃️ Rechnung erstellen":
    st.header("Neue Rechnung")
    dokument_typ = st.selectbox(
        "Dokumenttyp",
        ["Rechnung", "Kostenvoranschlag"],
        key="dokument_typ"
    )
    if st.session_state.get("edit_invoice_number") and \
        st.session_state.get("edit_loaded_for") != st.session_state["edit_invoice_number"]:

        data = get_invoice_by_number(st.session_state["edit_invoice_number"])

        if data:
            payload = data.get("payload", {})
            st.session_state["unternehmen"] = payload.get("unternehmen", "")
            # Kundendaten
            st.session_state["kunde_anrede"] = payload.get("kunde_anrede", "")
            st.session_state["kunde_name"] = payload.get("kunde_name", "")
            st.session_state["kunde_adresse"] = payload.get("kunde_adresse", "")
            st.session_state["kunde_ort"] = payload.get("kunde_ort", "")
            st.session_state["kunde_tel"] = payload.get("kunde_tel", "")

            # Fahrzeugdaten
            st.session_state["fahrzeug_marke"] = payload.get("fahrzeug_marke", "")
            st.session_state["fahrzeug_baujahr"] = payload.get("fahrzeug_baujahr", "")
            st.session_state["fahrzeug_farbe"] = payload.get("fahrzeug_farbe", "")
            st.session_state["fahrzeug_fin"] = payload.get("fahrzeug_fin", "")

            # Rechnung
            st.session_state["modus"] = payload.get("modus", "Brutto")
            st.session_state["rechnungsnr_index"] = payload.get("rechnungsnr_index", "")
            st.session_state["rechnungsdatum_obj"] = date.fromisoformat(
                payload.get("rechnungsdatum_obj")
            )

            # Positionen
            st.session_state["anzahl_positionen"] = payload.get("anzahl_positionen", 1)
            for i, pos in enumerate(payload.get("positionen", [])):
                st.session_state[f"beschreibung_{i}"] = pos.get("beschreibung", "")
                st.session_state[f"betrag_{i}"] = pos.get("summe", 0.0)

            # WICHTIG
            st.session_state["edit_loaded_for"] = st.session_state["edit_invoice_number"]

    
    # --- Auswahl des Unternehmens ---
    unternehmen = st.selectbox("Unternehmen auswählen", ["DellKuss", "Automobile Kuss"], key="unternehmen")
    # --- Unternehmensspezifische Daten ---
    if unternehmen == "DellKuss":
        logo_path = "assets/logo.png"
        firmendaten = ["David Kuss", "Edisonstr. 9", "86399 Bobingen"]
        kontakt = {
        "tel": "+49 157 58226071",
        "email": "kontakt@dellkuss.de",
        "web": "www.dellkuss.de"
        }
        fusszeile = [
            "dellkuss · Sparkasse Schwaben-Bodensee · IBAN DE92 7315 0000 1002 9247 83 · BIC BYLADEM1MLM",
            "Sitz der Firma: Bobingen, Deutschland · Inhaber: David Kuss · USt-IdNr. DE75392071642"
        ]
    else:
        logo_path = "assets/logo2.png"
        firmendaten = ["Automobile Kuss (Inh. David Kuss)", "Edisonstr. 9", "86399 Bobingen"]
        kontakt = {
        "tel": "+49 157 58226071",
        }
        fusszeile = [
            "Automobile Kuss · Sparkasse Schwaben-Bodensee · IBAN DE92 7315 0000 1002 9247 83 · BIC BYLADEM1MLM",
            "Sitz der Firma: Bobingen, Deutschland · Inhaber: David Kuss · USt-IdNr. DE75392071642"
        ]

    # --- Kundendaten ---
    st.subheader("🕴 Kundendaten")
    col1, col2 = st.columns(2)
    with col1:
        kunde_anrede = st.selectbox("Anrede", ["Herr", "Frau", "Firma"], key="kunde_anrede")
        kunde_name = st.text_input("Name / Firma", key="kunde_name")
        kunde_adresse = st.text_input("Straße und Hausnummer", key="kunde_adresse")
    with col2:
        kunde_ort = st.text_input("PLZ / Ort", key="kunde_ort")
        kunde_tel = st.text_input("Telefonnummer", key="kunde_tel")


    # --- Fahrzeugdaten ---
    st.subheader("🚗 Fahrzeugdaten")
    col1, col2 = st.columns(2)
    with col1:
        fahrzeug_marke = st.text_input("Marke / Typ", key="fahrzeug_marke")
        fahrzeug_farbe = st.text_input("Farbe", key="fahrzeug_farbe")
    with col2:
        fahrzeug_baujahr = st.text_input("Baujahr", key="fahrzeug_baujahr")
        fahrzeug_fin = st.text_input("Fahrgestellnummer (FIN)", key="fahrzeug_fin")

    # --- Leistungspositionen ---
    st.subheader("🛠️ Leistungspositionen")
    # --- Betragsmodus ---
    if "modus" not in st.session_state:
        st.session_state["modus"] = "Brutto"
    st.markdown("**Betragsmodus**")
    bcol1, bcol2, bcol3, _ = st.columns([0.12, 0.12, 0.12, 0.64])
    current = st.session_state.get("modus", "Brutto")
    with bcol1:
        if st.button("Brutto", key="modus_brutto"):
            st.session_state["modus"] = "Brutto"
    with bcol2:
        if st.button("Netto", key="modus_netto"):
            st.session_state["modus"] = "Netto"
    with bcol3:
        if st.button("Firma", key="modus_firma"):
            st.session_state["modus"] = "Firma"
    modus = st.session_state.get("modus", "Brutto")
    

    if dokument_typ == "Rechnung":
        rechnungsnr_index = st.text_input(
            "Rechnungsnr_Index",
            key="rechnungsnr_index"
        )
        if "rechnungsdatum_obj" not in st.session_state:
            st.session_state["rechnungsdatum_obj"] = date.today()
        rechnungsdatum_obj = st.date_input(
            "Rechnungsdatum",
            key="rechnungsdatum_obj"
        )
    else:
        rechnungsnr_index = None
        rechnungsdatum_obj = None

    if rechnungsdatum_obj:
        rechnungsdatum = rechnungsdatum_obj.strftime("%d.%m.%Y")
    else:
        rechnungsdatum = None
    rechnungsnummer_datum = rechnungsdatum

    if "anzahl_positionen" not in st.session_state:
        st.session_state["anzahl_positionen"] = 1
    st.number_input(
        "Anzahl der Positionen",
        min_value=1,
        max_value=1000,
        key="anzahl_positionen"
    )
    anzahl_positionen = st.session_state["anzahl_positionen"]

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
    st.subheader("💲 Gesamtsumme")
    summe_netto = sum([betrag for _, betrag in positionen])
    if modus == "Brutto":
        mwst = summe_netto * 0.19
        summe_brutto = summe_netto + mwst
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Summe netto (€)", f"{summe_netto:,.2f}")
        with col2: st.metric("MwSt (19%) (€)", f"{mwst:,.2f}")
        with col3: st.metric("Gesamtbetrag (€)", f"{summe_brutto:,.2f}")
    elif modus == "Netto":
        # Netto-Modus: nur Gesamtbetrag netto anzeigen, ohne MwSt
        mwst = 0.0
        summe_brutto = summe_netto
        col = st.columns(1)[0]
        col.metric("Gesamtbetrag netto (€)", f"{summe_netto:,.2f}")
    elif modus == "Firma":
        # Firma-Modus: wie Netto, aber Label "Betrag"
        mwst = 0.0
        summe_brutto = summe_netto
        col = st.columns(1)[0]
        col.metric("Betrag (€)", f"{summe_netto:,.2f}")

    # --- Aktionen ---
    st.subheader("🌌 Aktionen")
    from utils.pdf_generator_v2 import create_invoice_pdf
    if st.button("📄 PDF erstellen"):
        # --- Rechnungsnummer manuell zusammensetzen (neues Format: YYYY{index}) ---
        if dokument_typ == "Rechnung":
            index_clean = str(rechnungsnr_index).strip()
            jahr = rechnungsdatum_obj.year
            rechnungsnummer = f"{jahr}{index_clean}"
        else:
            rechnungsnummer = None

        buffer = BytesIO()

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
        if modus == "Brutto":
            mwst_val = summe_netto * 0.19
            brutto_val = summe_netto * 1.19
        elif modus == "Netto":
            # Netto-Modus: keine MwSt
            mwst_val = 0.0
            brutto_val = summe_netto
        elif modus == "Firma":
            # Firma-Modus: keine MwSt
            mwst_val = 0.0
            brutto_val = summe_netto

        summen = {
            "datum": rechnungsdatum,
            "rechnungsnummer": rechnungsnummer,
            "netto": summe_netto,
            "mwst": mwst_val,
            "brutto": brutto_val,
            "mode": modus
        }

        payload = {
            "unternehmen": unternehmen,
            "dokument_typ": dokument_typ,

            "kunde_anrede": kunde_anrede,
            "kunde_name": kunde_name,
            "kunde_adresse": kunde_adresse,
            "kunde_ort": kunde_ort,
            "kunde_tel": kunde_tel,

            "fahrzeug_marke": fahrzeug_marke,
            "fahrzeug_baujahr": fahrzeug_baujahr,
            "fahrzeug_farbe": fahrzeug_farbe,
            "fahrzeug_fin": fahrzeug_fin,

            "modus": modus,
            "rechnungsnr_index": rechnungsnr_index,
            "rechnungsdatum": rechnungsdatum,
            "rechnungsdatum_obj": rechnungsdatum_obj.isoformat() if rechnungsdatum_obj else None,

            "anzahl_positionen": int(anzahl_positionen),

            "positionen": positionen_liste
        }

        # -----------------------
        # 1. NUR Rechnung speichern
        # -----------------------
        if dokument_typ == "Rechnung":
            mode = "update" if st.session_state.get("edit_invoice_number") else "create"
            result = save_invoice(
                invoice_number=rechnungsnummer,
                invoice_date=rechnungsdatum_obj.isoformat(),
                customer_name=kunde_name,
                total=brutto_val,
                payload=payload,
                mode=mode
            )

            if result == "DUPLICATE_INVOICE_NUMBER":
                st.error("⚠️ Rechnungsnummer existiert bereits.")
            else:
                # Erfolgsmeldung
                if mode == "update":
                    st.success("✅ Rechnung aktualisiert.")
                else:
                    st.success("✅ Rechnung gespeichert.")
        # -----------------------
        # 2. PDF IMMER erzeugen
        # -----------------------
        # PDF erzeugen (IMMER, unabhängig von create/update)
        create_invoice_pdf(
            buffer,
            logo_path,
            kunde,
            fahrzeug,
            positionen_liste,
            summen,
            firmendaten,
            fusszeile,
            kontakt,
            dokument_typ=dokument_typ
        )

        buffer.seek(0)

        # Session State für Vorschau & Download
        st.session_state["pdf_buffer"] = buffer.getvalue()
        st.session_state["pdf_preview"] = base64.b64encode(buffer.getvalue()).decode()
        st.session_state["pdf_ready"] = True
        st.session_state["show_preview"] = False
        st.session_state["download_name"] = (
            f"Rechnung_{summen['rechnungsnummer']}.pdf"
            if dokument_typ == "Rechnung"
            else "Kostenvoranschlag.pdf"
        )

        # Edit-Modus sauber beenden
        st.session_state["is_edit_mode"] = False
        st.session_state["edit_loaded_for"] = None
        st.session_state.pop("edit_invoice_number", None)

    # =====================
    # PDF VORSCHAU + DOWNLOAD
    # =====================
    if "show_preview" not in st.session_state:
        st.session_state["show_preview"] = False

    if st.session_state.get("pdf_ready"):

        if st.button("👁️ PDF Vorschau"):
            st.session_state["show_preview"] = not st.session_state["show_preview"]

        if st.session_state["show_preview"]:
            st.markdown(
                f"""
                <iframe
                    src="data:application/pdf;base64,{st.session_state['pdf_preview']}"
                    width="60%"
                    height="850"
                    style="border-radius:10px; border:1px solid #ccc;"
                ></iframe>
                """,
                unsafe_allow_html=True
            )

        st.download_button(
            "📥 PDF herunterladen",
            data=st.session_state["pdf_buffer"],
            file_name=st.session_state["download_name"],
            mime="application/pdf"
        )

# ==============================
# ARCHIV
# ==============================
elif page == "🐙 Archiv":
    rows = get_all_invoices()

    if not rows:
        st.info("Noch keine Rechnungen gespeichert.")
    else:
        table_data = []

        for r in rows:
            # NEW tuple structure: id, invoice_number, invoice_date, customer_name, total
            _, nummer, datum, kunde, total = r

            table_data.append({
                "Rechnungsnummer": nummer,
                "Datum": datum,
                "Kunde": kunde,
                "Betrag": f"{total:.2f} €" if total else "0.00 €"
            })

        df = pd.DataFrame(table_data)

        # ==============================
        # FILTER
        # ==============================
        col1, col2 = st.columns(2)
        with col1:
            f_kunde = st.text_input("Kunde filtern")
        
        # Placeholder for layout if needed, or just remove col2
        with col2:
            st.write("") # Empty 

        filtered_df = df.copy()

        if f_kunde:
            filtered_df = filtered_df[
                filtered_df["Kunde"].str.contains(f_kunde, case=False, na=False)
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("Aktionen")

        selected_invoice = st.selectbox(
            "Rechnung auswählen",
            filtered_df["Rechnungsnummer"].tolist()
        )

        col_edit, col_delete = st.columns(2)

        # ---------- BEARBEITEN ----------
        with col_edit:
            if st.button("✏️ Bearbeiten"):
                st.session_state["edit_invoice_number"] = selected_invoice
                st.session_state["is_edit_mode"] = True
                st.session_state["navigate_to"] = "🗃️ Rechnung erstellen"
                st.rerun()

        # ---------- LÖSCHEN ----------
        with col_delete:
            if st.button("🗑️ Löschen") and "delete_candidate" not in st.session_state:
                st.session_state["delete_candidate"] = selected_invoice

        # ---------- BESTÄTIGUNG (ohne gelben Kasten) ----------
        if st.session_state.get("delete_candidate"):
            st.markdown(
                f"**Rechnung {st.session_state['delete_candidate']} wirklich löschen?**"
            )

            col_yes, col_no = st.columns(2)

            with col_yes:
                if st.button("✔ Ja, löschen", key="confirm_delete"):
                    delete_invoice(st.session_state["delete_candidate"])
                    del st.session_state["delete_candidate"]
                    st.rerun()

            with col_no:
                if st.button("❌ Abbrechen", key="cancel_delete"):
                    del st.session_state["delete_candidate"]
                    st.rerun()



st.markdown("---")
st.caption("© 2024 DellKuss – Der Dellendoktor")












