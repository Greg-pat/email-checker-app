import streamlit as st
from textblob import TextBlob
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')
spell = SpellChecker(language='en')

# ✅ Lista słów kluczowych do rozpoznawania formatu tekstu
EMAIL_KEYWORDS = ["dear", "yours sincerely", "yours faithfully", "regards", "best wishes", "please find attached"]
BLOG_KEYWORDS = ["today I want to share", "let me tell you", "I think", "in my opinion", "have you ever", "let’s talk about"]

# ✅ Funkcja do rozpoznawania formatu tekstu
def detect_format(email_text):
    text_lower = email_text.lower()
    email_count = sum(1 for word in EMAIL_KEYWORDS if word in text_lower)
    blog_count = sum(1 for word in BLOG_KEYWORDS if word in text_lower)

    if email_count > blog_count:
        return "E-mail"
    elif blog_count > email_count:
        return "Blog"
    else:
        return "Nieokreślony"

# ✅ Funkcja do oceny treści na podstawie podpunktów
def evaluate_content(email_text, required_points):
    points = 0
    covered = 0
    developed = 0
    text_lower = email_text.lower()

    for point in required_points:
        if any(phrase in text_lower for phrase in point):
            covered += 1
            if any(len(phrase.split()) > 2 for phrase in point):  
                developed += 1  

    # Ocena punktowa
    if covered == 3 and developed >= 2:
        points = 4
    elif covered == 3 and developed == 1:
        points = 3
    elif covered == 2 and developed >= 1:
        points = 2
    elif covered == 1:
        points = 1
    return points, covered, developed

# ✅ Funkcja do oceny spójności i logiki
def evaluate_coherence(email_text):
    sentences = email_text.split('.')
    if len(sentences) < 3:
        return 1, "Tekst jest za krótki. Dodaj więcej rozwinięć myśli."
    return 2, "Tekst jest dobrze zorganizowany."

# ✅ Funkcja do oceny zakresu środków językowych
def evaluate_language_range(email_text):
    words = email_text.split()
    unique_words = set(words)
    if len(unique_words) > len(words) * 0.6:
        return 2, "Zróżnicowane słownictwo. Bardzo dobrze!"
    return 1, "Słownictwo jest dość powtarzalne. Spróbuj dodać więcej synonimów."

# ✅ Funkcja do oceny poprawności językowej
def evaluate_correctness(email_text):
    matches = tool.check(email_text)
    grammar_errors = {}
    spell_errors = {}

    # Wykrywanie błędów gramatycznych (LanguageTool)
    for match in matches:
        error = match.context[match.offset:match.offset + match.errorLength]
        correction = match.replacements[0] if match.replacements else "Brak propozycji"
        grammar_errors[error] = (correction, "Błąd gramatyczny")

    # Wykrywanie błędów ortograficznych (pyspellchecker)
    misspelled_words = spell.unknown(email_text.split())
    for word in misspelled_words:
        correction = spell.correction(word) or "Brak propozycji"
        spell_errors[word] = (correction, "Błąd ortograficzny")

    # Łączymy błędy
    all_errors = {**grammar_errors, **spell_errors}
    
    # Punktacja
    error_count = len(all_errors)
    if error_count == 0:
        return 2, "Brak błędów! Doskonała poprawność językowa."
    elif error_count < 5:
        return 1, "Kilka drobnych błędów, ale nie wpływają znacząco na komunikację."
    return 0, "Zbyt dużo błędów – spróbuj je poprawić, aby tekst był bardziej zrozumiały."

# ✅ Główna funkcja oceny całego tekstu
def evaluate_email(email_text, task_requirements, selected_format):
    feedback = {}
    detected_format = detect_format(email_text)

    # Jeśli format się nie zgadza, ostrzeżenie
    if detected_format != "Nieokreślony" and detected_format != selected_format:
        feedback['📌 Uwaga!'] = f"Twój tekst wygląda jak **{detected_format}**, ale wybrałeś **{selected_format}**. Spróbuj dostosować styl."

    # Ocena każdego kryterium
    content_score, covered, developed = evaluate_content(email_text, task_requirements)
    coherence_score, coherence_feedback = evaluate_coherence(email_text)
    range_score, range_feedback = evaluate_language_range(email_text)
    correctness_score, correctness_feedback = evaluate_correctness(email_text)

    feedback['📝 Treść'] = f"{content_score}/4 - Odniosłeś się do {covered} podpunktów, {developed} rozwiniętych. Spróbuj dodać więcej szczegółów."
    feedback['🔗 Spójność i logika'] = f"{coherence_score}/2 - {coherence_feedback}"
    feedback['📖 Zakres językowy'] = f"{range_score}/2 - {range_feedback}"
    feedback['✅ Poprawność językowa'] = f"{correctness_score}/2 - {correctness_feedback}"

    return feedback, detected_format

# ✅ Interfejs użytkownika
st.title("📩 Automatyczna ocena pisemnych wypowiedzi")
st.write("✏️ Wybierz typ tekstu i sprawdź, czy spełnia kryteria egzaminacyjne.")

# ✅ Wybór formatu przez ucznia
selected_format = st.radio("Wybierz format tekstu:", ("E-mail", "Blog"))

# ✅ Treść wpisu
email_text = st.text_area("📌 Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        result, detected_format = evaluate_email(email_text, [['poinformować o terminie'], ['zaprosić na wydarzenie'], ['zapytać o szczegóły']], selected_format)

        # ✅ Wyświetlamy rzeczywisty format tekstu
        st.write(f"### 📖 Wykryty format tekstu: **{detected_format}**")
        if detected_format != selected_format:
            st.warning(f"⚠️ Twój tekst wygląda jak **{detected_format}**, ale wybrałeś **{selected_format}**. Spróbuj dostosować styl.")

        # ✅ Wyświetlanie wyników
        for key, value in result.items():
            st.write(f"**{key}:** {value}")

    else:
        st.warning("⚠️ Wpisz treść przed sprawdzeniem.")
