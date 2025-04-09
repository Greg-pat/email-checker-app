import streamlit as st
import language_tool_python
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime
import os

# Narzędzie do sprawdzania pisowni i gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# Logo i nagłówek
st.set_page_config(page_title="Ocena wypowiedzi pisemnej", layout="centered")
col1, col2 = st.columns([1, 8])
with col1:
    try:
        st.image("MindBloom jasne złoto zielony.png", width=120)
    except:
        st.markdown("### 🌱")
with col2:
    st.title("📧 Automatyczna ocena wypowiedzi pisemnej")
    st.markdown(f"**Data:** {datetime.now().strftime('%Y-%m-%d')}")

# Lista tematów egzaminacyjnych
TEMATY = {
    "Opisz swoje ostatnie wakacje": ["holiday", "trip", "beach", "mountains", "memories", "visited", "hotel"],
    "Napisz o swoich planach na najbliższy weekend": ["weekend", "going to", "plan", "cinema", "friends", "family"],
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": ["meet", "visit", "place", "Poland", "invite", "schedule"],
    "Opisz swój udział w szkolnym przedstawieniu": ["school play", "role", "stage", "acting", "performance", "nervous"],
    "Podziel się wrażeniami z wydarzenia szkolnego": ["event", "competition", "school", "experience", "memorable"],
    "Opisz swoje nowe hobby": ["hobby", "started", "enjoy", "benefits", "passion"],
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną": ["online learning", "advantages", "disadvantages", "difficult"],
    "Opisz szkolną wycieczkę, na której byłeś": ["school trip", "visited", "museum", "amazing", "historical"],
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": ["sightseeing", "places", "Poland", "tour", "recommend"]
}

# UWAGA: ścieżka do logo w PDF również musi być dostosowana:
LOGO_PDF_PATH = "MindBloom jasne złoto zielony.png"

def generuj_pdf(wyniki, tekst, temat):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.image(LOGO_PDF_PATH, x=10, y=8, w=40)
    except:
        pass
    pdf.set_font("Arial", size=12)
    pdf.ln(25)
    pdf.cell(200, 10, txt="Wyniki oceny wypowiedzi pisemnej", ln=True, align='C')
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Temat: {temat}")
    pdf.multi_cell(0, 10, f"Data: {datetime.now().strftime('%Y-%m-%d')}")
    for k, v in wyniki.items():
        pdf.multi_cell(0, 10, f"{k}: {v}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Treść pracy:")
    pdf.multi_cell(0, 10, tekst)
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer

# (reszta kodu pozostaje bez zmian — ocena i wyświetlanie wyników)
