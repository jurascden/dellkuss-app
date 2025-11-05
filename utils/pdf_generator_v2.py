from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import os

# ------------------------------------------------------------
# Layout-Konstanten (unverändert aus deiner perfekten Version)
# ------------------------------------------------------------
FOOTER_LINE1_Y = 60   # Hinweistext Überweisung
FOOTER_LINE2_Y = 40   # Fußdaten Firmendaten 1
FOOTER_LINE3_Y = 28   # Fußdaten Firmendaten 2

FOOTER_MARGIN_Y = 110     # Sicherheitsabstand zur Fußzeile
SUM_TOP_Y = FOOTER_LINE1_Y + 50
ITEMS_PER_PAGE = 20
LINE_HEIGHT = 14


# ------------------------------------------------------------
# Tabellenkopf & Footer (unverändert)
# ------------------------------------------------------------
def draw_table_header(c, width, height, header_y):
    c.setFont("Helvetica-Bold", 9)
    c.line(40, header_y + 5, width - 40, header_y + 5)
    c.drawString(40, header_y - 10, "Pos.")
    c.drawString(80, header_y - 10, "Beschreibung")
    c.drawString(width - 86, header_y - 10, "Gesamt (€)")
    c.line(40, header_y - 17, width - 40, header_y - 17)


def draw_footer(c, width, fusszeile=None):
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, FOOTER_LINE1_Y,
        "Bitte überweisen Sie den Rechnungsbetrag innerhalb von 14 Tagen nach Rechnungsdatum auf das unten stehende Geschäftskonto.")
    c.setFont("Helvetica", 7.5)
    if not fusszeile:
        fusszeile = ["dellkuss · Sparkasse Schwaben-Bodensee · IBAN DE92 7315 0000 1002 9247 83 · BIC BYLADEM1MLM",
            "Sitz der Firma: Bobingen, Deutschland · Geschäftsführung: David Kuss · USt-IdNr. DE75392071642"]
    c.drawCentredString(width / 2, FOOTER_LINE2_Y, fusszeile[0])
    c.drawCentredString(width / 2, FOOTER_LINE3_Y, fusszeile[1])


# ------------------------------------------------------------
# Hauptfunktion – identisches Layout, aber mit Streamlit-Daten
# ------------------------------------------------------------
def create_invoice_pdf(target, logo_path, kunde, fahrzeug, positionen, summen, firmendaten=None, fusszeile=None):
    """target: str/Pfad (lokal speichern) ODER file-like (BytesIO für Cloud/iPhone)"""
    c = canvas.Canvas(target, pagesize=A4)
    width, height = A4
    c.setTitle("Rechnung")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)

    # ------------------------------------------------------------
    # LOGO
    # ------------------------------------------------------------
    logo_x, logo_y, logo_width, logo_height = 40, height - 110, 210, 75
    if os.path.exists(logo_path):
        c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    # ------------------------------------------------------------
    # FIRMENDATEN (rechts, dynamisch)
    # ------------------------------------------------------------
    firmendaten_x = 400
    firmendaten_y = logo_y - 25
    line_height = 13.5
    if not firmendaten:
        firmendaten = ["dellkuss", "Edisonstr. 9", "86399 Bobingen"]
    for i, text in enumerate(firmendaten):
        c.drawString(firmendaten_x, firmendaten_y - (i * line_height), text)

    # ------------------------------------------------------------
    # KUNDENDATEN (links)
    # ------------------------------------------------------------
    kunden_x_left = 40
    kunden_y_start = firmendaten_y - 46

    c.drawString(kunden_x_left, kunden_y_start, kunde.get("anrede", ""))
    c.drawString(kunden_x_left, kunden_y_start - 14, kunde.get("name", ""))
    c.drawString(kunden_x_left, kunden_y_start - 28, kunde.get("adresse", ""))
    c.drawString(kunden_x_left, kunden_y_start - 42, kunde.get("ort", ""))

    # ------------------------------------------------------------
    # KONTAKTDATEN (rechts)
    # ------------------------------------------------------------
    kontakt_x_right = 400
    kontakt_y_start = kunden_y_start - 14
    c.drawString(kontakt_x_right, kontakt_y_start, "Tel.: 08234 / 123456")
    c.drawString(kontakt_x_right, kontakt_y_start - 14, "E-Mail: info@dellkuss.de")
    c.drawString(kontakt_x_right, kontakt_y_start - 28, "Web: www.dellkuss.de")

    # ------------------------------------------------------------
    # RECHNUNGS-INFOS
    # ------------------------------------------------------------
    c.setFont("Helvetica-Bold", 10)
    y_rechnung_titel = kontakt_y_start - 60
    c.drawString(40, y_rechnung_titel, "Rechnung")

    y_start_infos = y_rechnung_titel - 14
    c.setFont("Helvetica", 9)
    rechnungsnummer = summen.get("rechnungsnummer", "")
    c.drawString(40, y_start_infos, "Rechnungsnr.:")
    c.drawString(120, y_start_infos, rechnungsnummer)
    c.drawString(40, y_start_infos - 14, "Rechnungsdatum:")
    c.drawString(120, y_start_infos - 14, summen.get("datum", ""))

    # ------------------------------------------------------------
    # FAHRZEUGDATEN-BLOCK
    # ------------------------------------------------------------
    y_fahrzeug_start = y_start_infos - (14 * 3)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y_fahrzeug_start, "Fahrzeugdaten")
    c.setFont("Helvetica", 9)
    y_fahrzeug_details = y_fahrzeug_start - 14
    c.drawString(40, y_fahrzeug_details, "Marke/Typ:")
    c.drawString(120, y_fahrzeug_details, fahrzeug.get("marke", ""))
    c.drawString(40, y_fahrzeug_details - 14, "Baujahr/Farbe:")
    c.drawString(120, y_fahrzeug_details - 14,
                 f"{fahrzeug.get('baujahr', '')} / {fahrzeug.get('farbe', '')}")
    c.drawString(40, y_fahrzeug_details - 28, "FIN:")
    c.drawString(120, y_fahrzeug_details - 28, fahrzeug.get("fin", ""))

    # ------------------------------------------------------------
    # POSITIONEN-TABELLE
    # ------------------------------------------------------------
    c.setFont("Helvetica-Bold", 9)
    y_table_header = y_fahrzeug_details - 59
    draw_table_header(c, width, height, y_table_header)
    c.line(40, y_table_header + 5, width - 40, y_table_header + 5)
    c.line(40, y_table_header - 17, width - 40, y_table_header - 17)

    # ------------------------------------------------------------
    # POSITIONEN (mit Seiten- und Textumbruch)
    # ------------------------------------------------------------
    c.setFont("Helvetica", 9)
    start_y = y_table_header - 35
    lines_on_page = 0

    for i, pos in enumerate(positionen, start=1):
        beschreibung = pos.get("beschreibung", "")
        betrag = f"{pos.get('summe', 0):.2f}".replace(".", ",")
        y = start_y - (lines_on_page * LINE_HEIGHT)

        # Seitenumbruch
        if lines_on_page == ITEMS_PER_PAGE:
            draw_footer(c, width, fusszeile)
            c.showPage()
            new_header_y = height - 60
            c.setFont("Helvetica-Bold", 9)
            draw_table_header(c, width, height, new_header_y)
            c.setFont("Helvetica", 9)
            start_y = new_header_y - 35
            lines_on_page = 0
            y = start_y

        # Dynamischer Textumbruch
        max_width = width - 190
        words = beschreibung.split(" ")
        wrapped_lines = []
        current_line = ""
        for word in words:
            test_line = (current_line + " " + word).strip()
            if stringWidth(test_line, "Helvetica", 9) < max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = word
        if current_line:
            wrapped_lines.append(current_line)

        # Erste Zeile
        c.drawString(40, y, str(i))
        c.drawString(80, y, wrapped_lines[0])
        c.drawRightString(width - 40, y, betrag)

        # Weitere Zeilen
        extra_lines = len(wrapped_lines) - 1
        if extra_lines > 0:
            for j in range(1, len(wrapped_lines)):
                y_extra = y - (j * LINE_HEIGHT)
                c.drawString(80, y_extra, wrapped_lines[j])
            lines_on_page += extra_lines

        lines_on_page += 1
        y -= LINE_HEIGHT

    # ------------------------------------------------------------
    # SUMMENBLOCK (unverändert im Design)
    # ------------------------------------------------------------
    summe_netto = summen.get("netto", 0)
    ust = summen.get("mwst", 0)
    summe_brutto = summen.get("brutto", 0)

    y_sum_block = y - LINE_HEIGHT - 20
    c.line(width - 165, y_sum_block - 4, width - 40, y_sum_block - 4)
    c.line(width - 165, y_sum_block - 18, width - 40, y_sum_block - 18)

    c.setFont("Helvetica", 9)
    c.drawRightString(width - 100, y_sum_block, "Summe netto:")
    c.drawRightString(width - 40, y_sum_block,
                      f"{summe_netto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c.drawRightString(width - 100, y_sum_block - 14, "zzgl. USt. 19%:")
    c.drawRightString(width - 40, y_sum_block - 14,
                      f"{ust:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    y_end = y_sum_block - 28
    c.line(width - 165, y_end - 4, width - 40, y_end - 4)
    c.line(width - 165, y_end - 7, width - 40, y_end - 7)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width - 100, y_end, "Endsumme:")
    c.drawRightString(width - 40, y_end,
                      f"{summe_brutto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # ------------------------------------------------------------
    # FOOTER + ABSCHLUSS
    # ------------------------------------------------------------
    draw_footer(c, width, fusszeile)
    c.showPage()
    c.save()





