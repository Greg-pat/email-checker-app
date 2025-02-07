import streamlit as st
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')
spell = SpellChecker(language='en')

# ✅ Lista słów ignorowanych przez spellchecker (eliminacja fałszywych błędów)
IGNORE_WORDS = {"job", "you", "week", "news", "years", "media", "trends", "concerned", 
                "for", "position", "creative", "experience", "application", "manager", 
                "changes", "employer", "sincerely", "hard-working", "applications", 
                "trends,", "news,", "experience,", "creative,", "for.", "application."}

# ✅ Minimalna liczba słów dla każdego formatu
MIN_WORDS = {"E-mail": 50, "Blog": 75}

# ✅ Funkcja rozpoznająca format tekstu
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

# ✅ Funkcja oceniająca liczbę słów
def evaluate_word_count(email_text, format_type):
    words = email_text.split()
    word_count = len(words)
    min_words = MIN_WORDS.get(format_type, 50)

    if word_count >= min_words:
        return f"Liczba słów: {word_count}/{min_words} - Wystarczająca długość."
    else:
        return f"⚠️ Liczba słów: {word_count}/{min_words} - Za krótko. Dodaj więcej informacji."

# ✅ Funkcja oceniająca poprawność językową
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
    words_without_punctuation = [re.sub(r'[^\w\s]', '', word) for word in email_text.split()]
    misspelled_words = spell.unknown(words_without_punctuation)
    
    for word in misspelled_words:
        correction = spell.correction(word) or "Brak propozycji"
        if word.lower() in IGNORE_WORDS:
            continue  
        spell_errors[word] = (correction, "Błąd ortograficzny")

    all_errors = {**grammar_errors, **spell_errors, **punctuation_errors}
    errors_table = pd.DataFrame(
        [(error, correction, category) for error, (correction, category) in all_errors.items()],
        columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if all_errors else None

    error_count = len(all_errors)
    if error_count == 0:
        return 2, "Brak błędów! Doskonała poprawność językowa.", errors_table
    elif error_count < 5:
        return 1, "Kilka błędów, ale nie wpływają znacząco na komunikację.", errors_table
    return 0, "Zbyt dużo błędów – spróbuj je poprawić, aby tekst był bardziej zrozumiały.", errors_table

# ✅ Funkcja oceniająca spójność i logikę
def evaluate_coherence(email_text):
    sentences = email_text.split('.')
    if len(sentences) < 3:
        return 1, "Tekst jest za krótki. Dodaj więcej rozwinięć myśli."
    return 2, "Tekst jest dobrze zorganizowany."

# ✅ Funkcja oceniająca zakres językowy
def evaluate_language_range(email_text):
    words = email_text.split()
    unique_words = set(words)
    if len(unique_words) > len(words) * 0.6:
        return 2, "Zróżnicowane słownictwo. Bardzo dobrze!"
    return 1, "Słownictwo jest dość powtarzalne. Spróbuj dodać więcej synonimów."

# ✅ Główna funkcja oceny
def evaluate_email(email_text, selected_format):
    feedback = {}
    detected_format = detect_format(email_text)

    if detected_format != "Nieokreślony" and detected_format != selected_format:
        feedback['📌 Uwaga!'] = f"Twój tekst wygląda jak **{detected_format}**, ale wybrałeś **{selected_format}**. Spróbuj dostosować styl."

    feedback['📖 Liczba słów'] = evaluate_word_count(email_text, selected_format)

    coherence_score, coherence_feedback = evaluate_coherence(email_text)
    range_score, range_feedback = evaluate_language_range(email_text)
    correctness_score, correctness_feedback, errors_table = evaluate_correctness(email_text)

    feedback['Spójność i logika'] = f"{coherence_score}/2 - {coherence_feedback}"
    feedback['Zakres językowy'] = f"{range_score}/2 - {range_feedback}"
    feedback['Poprawność językowa'] = f"{correctness_score}/2 - {correctness_feedback}"

    return feedback, detected_format, errors_table

# ✅ Interfejs użytkownika
st.title("Automatyczna ocena wypowiedzi pisemnych wypowiedzi na egzamin ósmoklasisty.")
st.write("Wybierz typ tekstu i sprawdź, czy spełnia kryteria egzaminacyjne.")

selected_format = st.radio("Wybierz format tekstu:", ("E-mail", "Blog"))
email_text = st.text_area("Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        result, detected_format, errors_table = evaluate_email(email_text, selected_format)

        st.write(f"### Wykryty format tekstu: **{detected_format}**")
        for key, value in result.items():
            st.write(f"**{key}:** {value}")

        if errors_table is not None and not errors_table.empty:
            st.write("### ❌ Lista błędów i poprawek:")
            st.dataframe(errors_table, height=300, width=700)

    else:
        st.warning("⚠️ Wpisz treść przed sprawdzeniem.")
