# exam_checker_app.py
import streamlit as st
import pandas as pd
import language_tool_python
from datetime import date
import re

# Inicjalizacja lokalnego LanguageTool (działa offline, nie wymaga API)
tool = language_tool_python.LanguageTool('en-GB')

# Tematy i słowa kluczowe
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

# Analiza poprawności

def analiza_poprawnosci(tekst):
    matches = tool.check(tekst)
    bledy = []
    tekst_zaznaczony = tekst

    for match in matches:
        blad = tekst[match.offset: match.offset + match.errorLength]
        poprawka = match.replacements[0] if match.replacements else "-"
        if not blad.strip():
            continue
        tekst_zaznaczony = tekst_zaznaczony.replace(blad, f"**:red[{blad}]**", 1)
        bledy.append((blad, poprawka, match.ruleIssueType))

    tabela = pd.DataFrame(bledy, columns=["Błąd", "Poprawna forma", "Typ błędu"])
    pkt = 2 if len(bledy) == 0 else 1 if len(bledy) < 5 else 0
    return pkt, tabela, tekst_zaznaczony

# Ocena szczegółowa

def ocena_tresci(tekst, temat):
    slowa = TEMATY.get(temat, [])
    trafienia = sum(1 for s in slowa if s in tekst.lower())
    if trafienia >= 5: return 4, "Treść zgodna z tematem."
    if trafienia >= 3: return 3, "Dobra zgodność, ale można dodać szczegółów."
    if trafienia >= 2: return 2, "Częściowa zgodność."
    if trafienia == 1: return 1, "Tylko jeden aspekt tematu."
    return 0, "Treść niezgodna z tematem."

def ocena_spojnosci(tekst):
    if any(w in tekst.lower() for w in ["however", "then", "because", "first", "finally"]):
        return 2, "Użyto wyrażeń łączących."
    return 1, "Brakuje spójności logicznej."

def ocena_zakresu(tekst):
    sl = set(tekst.lower().split())
    if len(sl) > 40: return 2, "Bogaty zakres słów."
    if len(sl) > 20: return 1, "Słownictwo przeciętne."
    return 0, "Słownictwo bardzo ubogie."

def ocena_dlugosci(tekst):
    n = len(tekst.split())
    if 50 <= n <= 120:
        return 2, f"Liczba słów: {n} - poprawna."
    return 1 if n < 50 else 0, f"Liczba słów: {n} - poza zakresem."

# Streamlit UI
st.set_page_config("Ocena wypowiedzi pisemnej")
st.title("📩 Automatyczna ocena wypowiedzi pisemnej")
st.write(f"**Data:** {date.today().isoformat()}")

# Awatar coacha
st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px;'>
        <img src='https://cdn-icons-png.flaticon.com/512/4712/4712109.png' width='60'/>
        <span style='font-size: 18px;'>Cześć! Jestem Twoim trenerem pisania. Sprawdźmy Twój tekst razem! 💪</span>
    </div>
    <br>
""", unsafe_allow_html=True)

temat = st.selectbox("🎯 Wybierz temat:", list(TEMATY.keys()))
tekst = st.text_area("✍️ Wpisz tutaj swój tekst:")

if st.button("✅ Sprawdź"):
    pkt_tresc, op_tresc = ocena_tresci(tekst, temat)
    pkt_spojnosc, op_spojnosc = ocena_spojnosci(tekst)
    pkt_zakres, op_zakres = ocena_zakresu(tekst)
    pkt_dlugosc, op_dlugosc = ocena_dlugosci(tekst)
    pkt_popraw, tabela, zaznaczony = analiza_poprawnosci(tekst)

    suma = min(pkt_tresc + pkt_spojnosc + pkt_zakres + pkt_popraw + pkt_dlugosc, 10)

    st.header("📊 Wyniki oceny:")
    st.write(f"**Treść:** {pkt_tresc}/4 - {op_tresc}")
    st.write(f"**Spójność:** {pkt_spojnosc}/2 - {op_spojnosc}")
    st.write(f"**Zakres:** {pkt_zakres}/2 - {op_zakres}")
    st.write(f"**Poprawność:** {pkt_popraw}/2 - Im mniej błędów, tym lepiej!")
    st.write(f"**Długość:** {pkt_dlugosc}/2 - {op_dlugosc}")
    st.subheader(f"📌 Łączny wynik: {suma}/10 pkt")

    if not tabela.empty:
        st.subheader("❌ Lista błędów i poprawek:")
        st.dataframe(tabela)

    st.subheader("📝 Tekst z zaznaczonymi błędami:")
    st.markdown(zaznaczony, unsafe_allow_html=True)
