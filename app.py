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
                "changes", "employer", "sincerely", "hard-working", "applications"}

# ✅ Minimalna liczba słów dla każdego formatu
MIN_WORDS = {"E-mail": 50, "Blog": 75}

# ✅ Funkcja oceniająca treść
def ocena_treści(tekst):
    liczba_słów = len(tekst.split())
    if liczba_słów >= 60:
        return 4, "Treść dobrze rozwinięta, spełnia wszystkie podpunkty."
    elif liczba_słów >= 45:
        return 3, "Treść częściowo rozwinięta, brakuje szczegółów."
    elif liczba_słów >= 30:
        return 2, "Treść jest ogólna, niektóre punkty są zbyt krótkie."
    elif liczba_słów >= 15:
        return 1, "Treść bardzo skrócona, konieczne rozwinięcie."
    return 0, "Brak rozwinięcia treści."

# ✅ Funkcja oceniająca spójność i logikę
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

    punkty_treści, opis_treści = ocena_treści(tekst)
    punkty_spójności, opis_spójności = ocena_spójności(tekst)
    punkty_zakresu, opis_zakresu = ocena_zakresu(tekst)
    punkty_poprawności, opis_poprawności, tabela_błędów, tekst_zaznaczony = ocena_poprawności(tekst)

    # ✅ Pełna lista ocenianych kryteriów z oceną
    wyniki['📝 Treść'] = f"{punkty_treści}/4 - {opis_treści}"
    wyniki['🔗 Spójność i logika'] = f"{punkty_spójności}/2 - {opis_spójności}"
    wyniki['📖 Zakres językowy'] = f"{punkty_zakresu}/2 - {opis_zakresu}"
    wyniki['✅ Poprawność językowa'] = f"{punkty_poprawności}/2 - {opis_poprawności}"

    wyniki['📌 **Łączny wynik:**'] = f"🔹 **{punkty_treści + punkty_spójności + punkty_zakresu + punkty_poprawności}/10 pkt**"

    return wyniki, tabela_błędów, tekst_zaznaczony

# ✅ **Interfejs użytkownika**
st.set_page_config(page_title="Analiza tekstu", layout="centered")

st.title("📩 Automatyczna ocena pisemnych wypowiedzi")
selected_format = st.radio("Wybierz format tekstu:", ("E-mail", "Blog"))
email_text = st.text_area("📌 Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        wynik, tabela_błędów, tekst_zaznaczony = ocena_tekstu(email_text, selected_format)
        for klucz, wartość in wynik.items():
            st.write(f"**{klucz}:** {wartość}")
