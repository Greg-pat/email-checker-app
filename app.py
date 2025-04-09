import streamlit as st
import language_tool_python
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

# Narzędzie do sprawdzania pisowni i gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# Nagłówek
st.set_page_config(page_title="Ocena wypowiedzi pisemnej", layout="centered")
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

# (reszta kodu pozostaje bez zmian)
