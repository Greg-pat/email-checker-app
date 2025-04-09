import streamlit as st
import language_tool_python
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

# Narzędzie do sprawdzania pisowni i gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# Logo i nagłówek
st.set_page_config(page_title="Ocena wypowiedzi pisemnej", layout="centered")
col1, col2 = st.columns([1, 8])
with col1:
    st.image("/mnt/data/logo_mindbloom.jpg", width=100)
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

def ocena_liczby_slow(tekst):
    liczba = len(tekst.split())
    if 50 <= liczba <= 120:
        return 1, f"✅ Liczba słów: {liczba} - Poprawna długość."
    elif liczba < 50:
        return 0, f"⚠️ Liczba słów: {liczba} - Zbyt krótka wypowiedź."
    else:
        return 0, f"⚠️ Liczba słów: {liczba} - Zbyt długa wypowiedź."

def ocena_tresci(tekst, temat):
    if temat not in TEMATY:
        return 0, "Temat nieobsługiwany."
    kluczowe = TEMATY[temat]
    trafienia = sum(1 for slowo in kluczowe if slowo.lower() in tekst.lower())
    if trafienia >= 5:
        return 4, "Treść w pełni zgodna z tematem."
    elif trafienia >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif trafienia >= 2:
        return 2, "Częściowa zgodność."
    return 1 if trafienia == 1 else 0, "Treść niezgodna z tematem."

def ocena_spojnosci(tekst):
    if any(s in tekst.lower() for s in ["however", "therefore", "firstly", "in conclusion"]):
        return 2, "Tekst dobrze zorganizowany."
    return 1, "Spójność może być lepsza - użyj więcej wyrażeń łączących."

def ocena_zakresu(tekst):
    unikalne = set(tekst.lower().split())
    if len(unikalne) > 40:
        return 2, "Bogate słownictwo."
    return 1 if len(unikalne) > 20 else 0, "Zbyt proste słownictwo."

def ocena_poprawnosci(tekst):
    matches = tool.check(tekst)
    bledy = []
    tekst_zazn = tekst
    for match in matches:
        start = match.offset
        end = start + match.errorLength
        blad = tekst[start:end].strip()
        poprawka = match.replacements[0] if match.replacements else "Brak propozycji"
        if not blad: continue
        tekst_zazn = tekst_zazn.replace(blad, f"**:red[{blad}]**", 1)
        bledy.append((blad, poprawka, "Błąd gramatyczny"))
    tabela = pd.DataFrame(bledy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]) if bledy else None
    return 2 if len(bledy) == 0 else 1 if len(bledy) < 5 else 0, tabela, tekst_zazn

def generuj_pdf(wyniki, tekst, temat):
    pdf = FPDF()
    pdf.add_page()
    pdf.image("/mnt/data/logo_mindbloom.jpg", x=10, y=8, w=40)
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

def ocena_tekstu(tekst, temat):
    pkt_slow, info_slow = ocena_liczby_slow(tekst)
    pkt_tresc, info_tresc = ocena_tresci(tekst, temat)
    pkt_spojnosc, info_spojnosc = ocena_spojnosci(tekst)
    pkt_zakres, info_zakres = ocena_zakresu(tekst)
    pkt_poprawnosci, tabela, tekst_zazn = ocena_poprawnosci(tekst)
    suma = pkt_slow + pkt_tresc + pkt_spojnosc + pkt_zakres + pkt_poprawnosci
    wyniki = {
        "Zgodna ilość słów": f"{pkt_slow}/1 - {info_slow}",
        "Treść": f"{pkt_tresc}/4 - {info_tresc}",
        "Spójność i logika": f"{pkt_spojnosc}/2 - {info_spojnosc}",
        "Zakres językowy": f"{pkt_zakres}/2 - {info_zakres}",
        "Poprawność językowa": f"{pkt_poprawnosci}/2 - Im mniej błędów, tym lepiej!",
        "Łączny wynik": f"{suma}/10 pkt"
    }
    return wyniki, tabela, tekst_zazn, suma

selected_temat = st.selectbox("Wybierz temat:", list(TEMATY.keys()))
email_text = st.text_area("Wpisz swój tekst tutaj:")

if st.button("Sprawdź") and email_text:
    wynik, tabela, tekst_zaznaczony, suma = ocena_tekstu(email_text, selected_temat)
    st.subheader("Wyniki oceny:")
    for k, v in wynik.items():
        st.write(f"**{k}**: {v}")
    if tabela is not None:
        st.write("### Lista błędów i poprawek:")
        st.dataframe(tabela)
    st.write("### Tekst z zaznaczonymi błędami:")
    st.markdown(tekst_zaznaczony, unsafe_allow_html=True)
    pdf_data = generuj_pdf(wynik, email_text, selected_temat)
    st.download_button(label="📄 Pobierz raport PDF", data=pdf_data, file_name="raport_oceny.pdf")
