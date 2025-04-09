import streamlit as st
import pandas as pd
import re
from datetime import date

# Lista tematów i słów kluczowych
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

# Prosty słownik błędów - tylko przykłady
SLABY = {
    "hte": "the",
    "becuse": "because",
    "frend": "friend",
    "recieve": "receive",
    "wat": "what",
    "writting": "writing"
}

# Prosta analiza poprawności
def analiza_poprawnosci(tekst):
    bledy = []
    for slowo in tekst.split():
        czyste = re.sub(r'[^a-zA-Z]', '', slowo.lower())
        if czyste in SLABY:
            bledy.append((slowo, SLABY[czyste], "Literówka"))

    tekst_zaznaczony = tekst
    for blad, poprawka, _ in bledy:
        tekst_zaznaczony = tekst_zaznaczony.replace(blad, f"**:red[{blad}]**", 1)

    tabela = pd.DataFrame(bledy, columns=["Błąd", "Poprawna forma", "Typ błędu"])
    return 2 if len(bledy) == 0 else 1 if len(bledy) < 5 else 0, tabela, tekst_zaznaczony

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

# UI Streamlit
st.set_page_config("Ocena wypowiedzi pisemnej")
st.title("📩 Automatyczna ocena wypowiedzi pisemnej")
st.write(f"**Data:** {date.today().isoformat()}")

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
    st.write(f"**Poprawność:** {pkt_popraw}/2 - {'Im mniej błędów, tym lepiej!'}")
    st.write(f"**Długość:** {pkt_dlugosc}/2 - {op_dlugosc}")
    st.subheader(f"📌 Łączny wynik: {suma}/10 pkt")

    if not tabela.empty:
        st.subheader("❌ Lista błędów i poprawek:")
        st.dataframe(tabela)

    st.subheader("📝 Tekst z zaznaczonymi błędami:")
    st.markdown(zaznaczony, unsafe_allow_html=True)
