import streamlit as st
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki (British English)
tool = language_tool_python.LanguageToolPublicAPI('en-GB')
spell = SpellChecker(language='en')

# ✅ Rozszerzona lista tematów egzaminacyjnych i wymagane słownictwo
TEMATY = {
    "Opisz swoje ostatnie wakacje": ["holiday", "trip", "beach", "mountains", "memories", "visited", "hotel"],
    "Napisz o swoich planach na najbliższy weekend": ["weekend", "going to", "plan", "cinema", "friends", "family"],
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": ["meet", "visit", "place", "Poland", "invite", "schedule"],
    "Opisz swój udział w szkolnym przedstawieniu": ["school play", "role", "stage", "acting", "performance", "nervous"],
    "Podziel się wrażeniami z wydarzenia szkolnego": ["school event", "competition", "trip", "concert", "experience"],
    "Zachęć kolegę do udziału w wydarzeniu w jego szkole": ["should", "join", "fun", "great opportunity", "experience"],
    "Opisz swoje nowe hobby": ["hobby", "started", "fun", "interesting", "skills", "passion"],
    "Zachęć znajomego do spróbowania Twojego hobby": ["try", "exciting", "enjoy", "recommend", "great", "fun"],
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną": ["online learning", "advantages", "disadvantages", "difficult"],
    "Zapytaj kolegę o jego opinię na temat nauki zdalnej": ["online classes", "do you like", "opinion", "better", "pros and cons"],
    "Opisz szkolną wycieczkę, na której byłeś": ["school trip", "visited", "museum", "amazing", "historical"],
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": ["tour", "sightseeing", "historical", "beautiful places"]
}

# ✅ Funkcja oceniająca zgodność z tematem
def ocena_treści(tekst, temat):
    if temat not in TEMATY:
        return 0, "Nie wybrano tematu lub temat nieobsługiwany."

    słowa_kluczowe = TEMATY[temat]
    liczba_wystąpień = sum(1 for słowo in słowa_kluczowe if słowo.lower() in tekst.lower())

    if liczba_wystąpień >= 5:
        return 4, "Treść w pełni zgodna z tematem. Świetnie!"
    elif liczba_wystąpień >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif liczba_wystąpień >= 2:
        return 2, "Częściowa zgodność, rozwinięcie tematu jest niewystarczające."
    return 1 if liczba_wystąpień == 1 else 0, "Treść nie jest zgodna z tematem."

# ✅ Funkcja oceniająca liczbę słów
def ocena_liczby_słów(tekst):
    liczba_słów = len(tekst.split())

    if 50 <= liczba_słów <= 120:
        return 2, f"✅ Liczba słów: {liczba_słów} - Poprawna długość."
    return 1, f"⚠️ Liczba słów: {liczba_słów} - Powinno być między 50 a 120."

# ✅ Funkcja oceniająca poprawność językową i podkreślająca błędy
def ocena_poprawności(tekst):
    matches = tool.check(tekst)
    błędy = []
    tekst_zaznaczony = tekst

    for match in matches:
        start = match.offset
        end = start + match.errorLength
        błąd = tekst[start:end]
        poprawka = match.replacements[0] if match.replacements else "Brak propozycji"

        if błąd.strip() == "":
            continue  

        tekst_zaznaczony = re.sub(
            rf'\b{re.escape(błąd)}\b',
            f"<span style='color:red; font-weight:bold;'>{błąd}</span>",
            tekst_zaznaczony,
            count=1
        )

        błędy.append((błąd, poprawka, "Błąd gramatyczny"))

    tabela_błędów = pd.DataFrame(
        błędy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if błędy else None

    return 2 if len(błędy) == 0 else 1 if len(błędy) < 5 else 0, tabela_błędów, tekst_zaznaczony

# ✅ Główna funkcja oceny
def ocena_tekstu(tekst, temat):
    punkty_słów, opis_słów = ocena_liczby_słów(tekst)
    punkty_treści, opis_treści = ocena_treści(tekst, temat)
    punkty_poprawności, tabela_błędów, tekst_zaznaczony = ocena_poprawności(tekst)

    # 🔥 **Obliczamy poprawnie sumę punktów (max. 10/10)**
    suma_punktów = punkty_słów + punkty_treści + punkty_poprawności
    suma_punktów = min(suma_punktów, 10)  # ✅ Nie może przekroczyć 10 pkt

    wyniki = {
        '📖 Zgodna ilość słów': f"{punkty_słów}/2 - {opis_słów}",
        '📝 Treść': f"{punkty_treści}/4 - {opis_treści}",
        '✅ Poprawność językowa': f"{punkty_poprawności}/2 - Im mniej błędów, tym lepiej!",
        '📌 **Łączny wynik:**': f"🔹 **{suma_punktów}/10 pkt**"
    }
    
    return wyniki, tabela_błędów, tekst_zaznaczony

# ✅ **Interfejs użytkownika**
st.set_page_config(page_title="Ocena pisemnych wypowiedzi", layout="centered")

st.title("📩 Automatyczna ocena pisemnych wypowiedzi")
selected_temat = st.selectbox("📌 Wybierz temat:", list(TEMATY.keys()))
email_text = st.text_area("✏️ Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        wynik, tabela_błędów, tekst_zaznaczony = ocena_tekstu(email_text, selected_temat)

        st.subheader("📊 Wyniki oceny:")
        for klucz, wartość in wynik.items():
            st.write(f"**{klucz}:** {wartość}")

        if tabela_błędów is not None and not tabela_błędów.empty:
            st.write("### ❌ Lista błędów i poprawek:")
            st.dataframe(tabela_błędów, height=300, width=700)

        st.write("### 🔍 Tekst z zaznaczonymi błędami:")
        st.markdown(f"<p style='font-size:16px;'>{tekst_zaznaczony}</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Wpisz tekst przed sprawdzeniem.")
