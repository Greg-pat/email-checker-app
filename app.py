import streamlit as st
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki (British English)
tool = language_tool_python.LanguageToolPublicAPI('en-GB')
spell = SpellChecker(language='en')

# ✅ Lista słów ignorowanych przez spellchecker (eliminacja fałszywych błędów)
IGNORE_WORDS = {"job", "you", "week", "news", "years", "media", "trends", "concerned", 
                "for", "position", "creative", "experience", "application", "manager", 
                "changes", "employer", "sincerely", "hard-working", "applications", 
                "trends,", "news,", "experience,", "creative,", "for.", "application."}

# ✅ Minimalna liczba słów dla każdego formatu
MIN_WORDS = {"E-mail": 50, "Blog": 75}

# ✅ Funkcja oceniająca liczbę słów
def ocena_liczby_słów(tekst, typ):
    słowa = tekst.split()
    liczba_słów = len(słowa)
    min_słów = MIN_WORDS.get(typ, 50)

    if liczba_słów >= min_słów:
        return f"✅ Liczba słów: {liczba_słów}/{min_słów} - Wystarczająca długość."
    else:
        return f"⚠️ Liczba słów: {liczba_słów}/{min_słów} - Za krótko. Dodaj więcej szczegółów."

# ✅ Funkcja oceniająca poprawność językową i podkreślająca błędy
def ocena_poprawności(tekst):
    matches = tool.check(tekst)
    błędy_gramatyczne = {}
    błędy_ortograficzne = {}
    błędy_interpunkcyjne = {}
    tekst_zaznaczony = tekst

    for match in matches:
        błąd = match.context[match.offset:match.offset + match.errorLength]
        poprawka = match.replacements[0] if match.replacements else "Brak propozycji"

        if błąd.lower() in IGNORE_WORDS or len(błąd) < 2:
            continue

        if match.ruleId.startswith("PUNCTUATION") or match.ruleId.startswith("TYPOGRAPHY"):
            błędy_interpunkcyjne[błąd] = (poprawka, "Błąd interpunkcyjny")
        else:
            błędy_gramatyczne[błąd] = (poprawka, "Błąd gramatyczny")

        tekst_zaznaczony = re.sub(rf'\b{re.escape(błąd)}\b', f"<span style='color:red; font-weight:bold;'>{błąd}</span>", tekst_zaznaczony, 1)

    słowa_bez_interpunkcji = [re.sub(r'[^\w\s]', '', word) for word in tekst.split()]
    błędne_słowa = spell.unknown(słowa_bez_interpunkcji)

    for słowo in błędne_słowa:
        poprawka = spell.correction(słowo) or "Brak propozycji"
        if słowo.lower() in IGNORE_WORDS:
            continue  
        błędy_ortograficzne[słowo] = (poprawka, "Błąd ortograficzny")
        tekst_zaznaczony = re.sub(rf'\b{re.escape(słowo)}\b', f"<span style='color:red; font-weight:bold;'>{słowo}</span>", tekst_zaznaczony, 1)

    wszystkie_błędy = {**błędy_gramatyczne, **błędy_ortograficzne, **błędy_interpunkcyjne}
    tabela_błędów = pd.DataFrame(
        [(błąd, poprawka, kategoria) for błąd, (poprawka, kategoria) in wszystkie_błędy.items()],
        columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if wszystkie_błędy else None

    liczba_błędów = len(wszystkie_błędy)
    if liczba_błędów == 0:
        return 2, "Brak błędów! Doskonała poprawność językowa.", tabela_błędów, tekst_zaznaczony
    elif liczba_błędów < 5:
        return 1, "Kilka błędów, ale nie wpływają znacząco na komunikację.", tabela_błędów, tekst_zaznaczony
    return 0, "Zbyt dużo błędów – spróbuj je poprawić, aby poprawić zrozumiałość.", tabela_błędów, tekst_zaznaczony

# ✅ Główna funkcja oceny
def ocena_tekstu(tekst, format):
    wyniki = {}

    wyniki['📖 Liczba słów'] = ocena_liczby_słów(tekst, format)

    punkty_poprawności, opis_poprawności, tabela_błędów, tekst_zaznaczony = ocena_poprawności(tekst)

    wyniki['✅ Poprawność językowa'] = f"{punkty_poprawności}/2 - {opis_poprawności}"

    wyniki['📌 **Łączny wynik:**'] = f"🔹 **{punkty_poprawności}/10 pkt**"

    return wyniki, tabela_błędów, tekst_zaznaczony

# ✅ **Interfejs użytkownika**
st.title("📩 Automatyczna ocena pisemnych wypowiedzi")
st.write("✏️ Wybierz typ tekstu i sprawdź, czy spełnia kryteria egzaminacyjne.")

selected_format = st.radio("Wybierz format tekstu:", ("E-mail", "Blog"))
email_text = st.text_area("📌 Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        wynik, tabela_błędów, tekst_zaznaczony = ocena_tekstu(email_text, selected_format)

        for klucz, wartość in wynik.items():
            st.write(f"**{klucz}:** {wartość}")

        if tabela_błędów is not None and not tabela_błędów.empty:
            st.write("### ❌ Lista błędów i poprawek:")
            st.dataframe(tabela_błędów, height=300, width=700)

        st.write("### 🔍 Tekst z zaznaczonymi błędami:")
        st.markdown(f"<p style='font-size:16px;'>{tekst_zaznaczony}</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Wpisz tekst przed sprawdzeniem.")
