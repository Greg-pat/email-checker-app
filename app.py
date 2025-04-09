import streamlit as st
import language_tool_python
import pandas as pd

# Narzędzie do sprawdzania pisowni i gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

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
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": ["sightseeing", "places", "Poland", "tour", "recommend"],
}

# Ocena liczby słów

def ocena_liczby_słów(tekst):
    liczba = len(tekst.split())
    if 50 <= liczba <= 120:
        return 2, f"✅ Liczba słów: {liczba} – Poprawna długość."
    elif liczba < 50:
        return 1, f"⚠️ Liczba słów: {liczba} – Zbyt krótka wypowiedź."
    else:
        return 1, f"⚠️ Liczba słów: {liczba} – Zbyt długa wypowiedź (max 120 słów)."

# Ocena treści

def ocena_treści(tekst, temat):
    if temat not in TEMATY:
        return 0, "Nie wybrano tematu lub temat nieobsługiwany."
    kluczowe = TEMATY[temat]
    trafienia = sum(1 for slowo in kluczowe if slowo.lower() in tekst.lower())
    if trafienia >= 5:
        return 4, "Treść w pełni zgodna z tematem. Świetnie!"
    elif trafienia >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif trafienia >= 2:
        return 2, "Częściowa zgodność, rozwinięcie tematu jest niewystarczające."
    return 1 if trafienia == 1 else 0, "Treść nie jest zgodna z tematem."

# Spójność i logika

def ocena_spójności(tekst):
    if any(s in tekst.lower() for s in ["however", "therefore", "firstly", "in conclusion"]):
        return 2, "Tekst jest dobrze zorganizowany."
    return 1, "Spójność może być lepsza – użyj więcej wyrażeń łączących."

# Zakres środków językowych

def ocena_zakresu(tekst):
    unikalne = set(tekst.lower().split())
    if len(unikalne) > 40:
        return 2, "Bardzo bogate słownictwo!"
    return 1 if len(unikalne) > 20 else 0, "Słownictwo jest zbyt proste."

# Poprawność językowa

def ocena_poprawności(tekst):
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

# Ocena łączna

def ocena_tekstu(tekst, temat):
    pkt_slow, opis_slow = ocena_liczby_słów(tekst)
    pkt_tresc, opis_tresc = ocena_treści(tekst, temat)
    pkt_spojnosc, opis_spojnosc = ocena_spójności(tekst)
    pkt_zakres, opis_zakres = ocena_zakresu(tekst)
    pkt_poprawnosci, tabela, tekst_zazn = ocena_poprawności(tekst)

    suma = min(pkt_slow + pkt_tresc + pkt_spojnosc + pkt_zakres + pkt_poprawnosci, 10)

    wyniki = {
        "📖 Zgodna liczba słów": f"{pkt_slow}/2 - {opis_slow}",
        "📝 Treść": f"{pkt_tresc}/4 - {opis_tresc}",
        "🔗 Spójność i logika": f"{pkt_spojnosc}/2 - {opis_spojnosc}",
        "📖 Zakres językowy": f"{pkt_zakres}/2 - {opis_zakres}",
        "✅ Poprawność językowa": f"{pkt_poprawnosci}/2 - Im mniej błędów, tym lepiej!",
        "📌 Łączny wynik::": f"🔹 {suma}/10 pkt"
    }

    return wyniki, tabela, tekst_zazn

# Streamlit UI
st.set_page_config(page_title="Ocena wypowiedzi pisemnej", layout="centered")
st.title("📧 Automatyczna ocena wypowiedzi pisemnej")

selected_temat = st.selectbox("📌 Wybierz temat:", list(TEMATY.keys()))
email_text = st.text_area("✏️ Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        wynik, tabela_bledow, tekst_zaznaczony = ocena_tekstu(email_text, selected_temat)

        st.subheader(":bar_chart: Wyniki oceny:")
        for klucz, wartosc in wynik.items():
            st.write(f"**{klucz}**: {wartosc}")

        if tabela_bledow is not None:
            st.write("### ❌ Lista błędów i poprawek:")
            st.dataframe(tabela_bledow, use_container_width=True)

        st.write("### 🔍 Tekst z zaznaczonymi błędami:")
        st.markdown(tekst_zaznaczony, unsafe_allow_html=True)
