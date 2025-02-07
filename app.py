import streamlit as st
from textblob import TextBlob
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')
spell = SpellChecker(language='en')

# ✅ Słowa ignorowane (fałszywe błędy)
IGNORE_WORDS = {"job", "you", "week", "news", "years", "media", "trends", "concerned", 
                "for", "position", "creative", "experience", "application", "manager", 
                "changes", "employer", "sincerely"}

# ✅ Funkcja do rozpoznawania formatu tekstu (E-mail vs Blog)
def detect_format(email_text):
    email_keywords = ["dear", "yours sincerely", "yours faithfully", "regards", "best wishes", "please find attached"]
    blog_keywords = ["today I want to share", "let me tell you", "I think", "in my opinion", "have you ever", "let’s talk about"]

    text_lower = email_text.lower()
    email_count = sum(1 for word in email_keywords if word in text_lower)
    blog_count = sum(1 for word in blog_keywords if word in text_lower)

    if email_count > blog_count:
        return "E-mail"
    elif blog_count > email_count:
        return "Blog"
    else:
        return "Nieokreślony"

# ✅ Funkcja do oceny poprawności językowej
def evaluate_correctness(email_text):
    matches = tool.check(email_text)
    grammar_errors = {}
    spell_errors = {}
    punctuation_errors = {}

    # ✅ Wykrywanie błędów gramatycznych (LanguageTool)
    for match in matches:
        error = match.context[match.offset:match.offset + match.errorLength]
        correction = match.replacements[0] if match.replacements else "Brak propozycji"

        if error.lower() in IGNORE_WORDS or len(error) < 2:
            continue

        if match.ruleId.startswith("PUNCTUATION") or match.ruleId.startswith("TYPOGRAPHY"):
            punctuation_errors[error] = (correction, "Błąd interpunkcyjny")
        else:
            grammar_errors[error] = (correction, "Błąd gramatyczny")

    # ✅ Wykrywanie błędów ortograficznych (pyspellchecker)
    misspelled_words = spell.unknown(email_text.split())
    for word in misspelled_words:
        correction = spell.correction(word) or "Brak propozycji"
        if word.lower() in IGNORE_WORDS:
            continue  
        spell_errors[word] = (correction, "Błąd ortograficzny")

    # ✅ Tworzenie tabeli błędów
    all_errors = {**grammar_errors, **spell_errors, **punctuation_errors}
    errors_table = pd.DataFrame(
        [(error, correction, category) for error, (correction, category) in all_errors.items()],
        columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if all_errors else None

    # ✅ Punktacja
    error_count = len(all_errors)
    if error_count == 0:
        return 2, "Brak błędów! Doskonała poprawność językowa.", errors_table
    elif error_count < 5:
        return 1, "Kilka drobnych błędów, ale nie wpływają znacząco na komunikację.", errors_table
    return 0, "Zbyt dużo błędów – spróbuj je poprawić, aby tekst był bardziej zrozumiały.", errors_table

# ✅ Główna funkcja oceny tekstu
def evaluate_email(email_text, selected_format):
    feedback = {}
    detected_format = detect_format(email_text)

    # ✅ Ostrzeżenie jeśli format się nie zgadza
    if detected_format != "Nieokreślony" and detected_format != selected_format:
        feedback['📌 Uwaga!'] = f"Twój tekst wygląda jak **{detected_format}**, ale wybrałeś **{selected_format}**. Spróbuj dostosować styl."

    # ✅ Ocena poprawności językowej
    correctness_score, correctness_feedback, errors_table = evaluate_correctness(email_text)

    # ✅ Wyniki punktowe
    feedback['✅ Poprawność językowa'] = f"{correctness_score}/2 - {correctness_feedback}"

    return feedback, detected_format, errors_table

# ✅ Interfejs użytkownika
st.title("📩 Automatyczna ocena pisemnych wypowiedzi")
st.write("✏️ Wybierz typ tekstu i sprawdź, czy spełnia kryteria egzaminacyjne.")

# ✅ Wybór formatu
selected_format = st.radio("Wybierz format tekstu:", ("E-mail", "Blog"))

# ✅ Treść wpisu
email_text = st.text_area("📌 Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        result, detected_format, errors_table = evaluate_email(email_text, selected_format)

        # ✅ Wyświetlamy rzeczywisty format tekstu
        st.write(f"### 📖 Wykryty format tekstu: **{detected_format}**")
        if detected_format != selected_format:
            st.warning(f"⚠️ Twój tekst wygląda jak **{detected_format}**, ale wybrałeś **{selected_format}**. Spróbuj dostosować styl.")

        # ✅ Wyświetlanie wyników
        for key, value in result.items():
            st.write(f"**{key}:** {value}")

        # ✅ Tabela błędów
        if errors_table is not None and not errors_table.empty:
            st.write("### ❌ Lista błędów i poprawek:")
            st.dataframe(errors_table, height=300, width=700)

    else:
        st.warning("⚠️ Wpisz treść przed sprawdzeniem.")
