import streamlit as st
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki (British English)
tool = language_tool_python.LanguageToolPublicAPI('en-GB')
spell = SpellChecker(language='en')

# ✅ Tematy i wymagane słowa kluczowe
TEMATY = {
    "Blog o nowinkach technicznych": ["technology", "innovation", "AI", "robot", "device", "software", "gadget"],
    "E-mail o spotkaniu klasowym": ["meeting", "class", "school", "date", "time", "place", "invitation"]
}

# ✅ Funkcja oceniająca liczbę słów
def ocena_liczby_słów(tekst):
    liczba_słów = len(tekst.split())

    if 50 <= liczba_słów <= 120:
        return 2, f"✅ Liczba słów: {liczba_słów} - Poprawna długość."
    return 1, f"⚠️ Liczba słów: {liczba_słów} - Powinno być między 50 a 120."

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

# ✅ Funkcja oceniająca spójność i logikę wypowiedzi
def ocena_spójności(tekst):
    zdania = tekst.split('.')
    if len(zdania) >= 4:
        return 2, "Tekst jest dobrze zorganizowany i logiczny."
    elif len(zdania) >= 2:
        return 1, "Tekst zawiera pewne luki w spójności."
    return 0, "Tekst niespójny, wymaga lepszego uporządkowania."

# ✅ Funkcja oceniająca zakres językowy
def ocena_zakresu(tekst):
    słowa = tekst.split()
    unikalne_słowa = set(słowa)
    if len(unikalne_słowa) > len(słowa) * 0.6:
        return 2, "Zróżnicowane słownictwo. Bardzo dobrze!"
    return 1, "Słownictwo jest dość powtarzalne. Spróbuj dodać więcej synonimów."

# ✅ Funkcja oceniająca poprawność językową i podkreślająca błędy
def ocena_poprawności(tekst):
    matches = tool.check(tekst)
    błędy = []
    tekst_zaznaczony = tekst

    for match in matches:
        błąd = match.context[match.offset:match.offset + match.errorLength]
        poprawka = match.replacements[0] if match.replacements else "Brak propozycji"
        błędy.append((błąd, poprawka, "Błąd gramatyczny"))
        tekst_zaznaczony = tekst_zaznaczony.replace(błąd, f"<span style='color:red; font-weight:bold;'>{błąd}</span>")

    tabela_błędów = pd.DataFrame(błędy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]) if błędy else None

    return 2 if len(błędy) == 0 else 1 if len(błędów) < 5 else 0, tabela_błędów, tekst_zaznaczony

# ✅ Główna funkcja oceny
def ocena_tekstu(tekst, temat):
    punkty_słów, opis_słów = ocena_liczby_słów(tekst)
    punkty_treści, opis_treści = ocena_treści(tekst, temat)
    punkty_spójności, opis_spójności = ocena_spójności(tekst)
    punkty_zakresu, opis_zakresu = ocena_zakresu(tekst)
    punkty_poprawności, tabela_błędów, tekst_zaznaczony = ocena_poprawności(tekst)

    wyniki = {
        '📖 Zgodna ilość słów': f"{punkty_słów}/2 - {opis_słów}",
        '📝 Treść': f"{punkty_treści}/4 - {opis_treści}",
        '🔗 Spójność i logika': f"{punkty_spójności}/2 - {opis_spójności}",
        '📖 Zakres środków językowych': f"{punkty_zakresu}/2 - {opis_zakresu}",
        '✅ Poprawność językowa': f"{punkty_poprawności}/2 - Im mniej błędów, tym lepiej!",
        '📌 **Łączny wynik:**': f"🔹 **{punkty_słów + punkty_treści + punkty_spójności + punkty_zakresu + punkty_poprawności}/10 pkt**"
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
