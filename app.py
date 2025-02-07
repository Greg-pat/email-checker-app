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

# ✅ Funkcja oceniająca liczbę słów
def evaluate_word_count(email_text, format_type):
    words = email_text.split()
    word_count = len(words)
    min_words = MIN_WORDS.get(format_type, 50)

    if word_count >= min_words:
        return f"✅ Liczba słów: {word_count}/{min_words} - Wystarczająca długość."
    else:
        return f"⚠️ Liczba słów: {word_count}/{min_words} - Za krótko. Dodaj więcej informacji."

# ✅ Funkcja oceniająca poprawność językową i podkreślająca błędy
def evaluate_correctness(email_text):
    matches = tool.check(email_text)
    grammar_errors = {}
    spell_errors = {}
    punctuation_errors = {}
    highlighted_text = email_text

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

        # ✅ Podkreślanie błędów w tekście na czerwono
        highlighted_text = re.sub(rf'\b{re.escape(error)}\b', f"<span style='color:red; font-weight:bold;'>{error}</span>", highlighted_text, 1)

    # ✅ Wykrywanie błędów ortograficznych (pyspellchecker)
    words_without_punctuation = [re.sub(r'[^\w\s]', '', word) for word in email_text.split()]
    misspelled_words = spell.unknown(words_without_punctuation)
    
    for word in misspelled_words:
        correction = spell.correction(word) or "Brak propozycji"
        if word.lower() in IGNORE_WORDS:
            continue  
        spell_errors[word] = (correction, "Błąd ortograficzny")

        # ✅ Podkreślanie błędów ortograficznych w tekście na czerwono
        highlighted_text = re.sub(rf'\b{re.escape(word)}\b', f"<span style='color:red; font-weight:bold;'>{word}</span>", highlighted_text, 1)

    all_errors = {**grammar_errors, **spell_errors, **punctuation_errors}
    errors_table = pd.DataFrame(
        [(error, correction, category) for error, (correction, category) in all_errors.items()],
        columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if all_errors else None

    error_count = len(all_errors)
    if error_count == 0:
        return 2, "Brak błędów! Doskonała poprawność językowa.", errors_table, highlighted_text
    elif error_count < 5:
        return 1, "Kilka błędów, ale nie wpływają znacząco na komunikację.", errors_table, highlighted_text
    return 0, "Zbyt dużo błędów – spróbuj je poprawić, aby tekst był bardziej zrozumiały.", errors_table, highlighted_text

# ✅ Główna funkcja oceny
def evaluate_email(email_text, selected_format):
    feedback = {}

    feedback['📖 Liczba słów'] = evaluate_word_count(email_text, selected_format)

    correctness_score, correctness_feedback, errors_table, highlighted_text = evaluate_correctness(email_text)

    feedback['✅ Poprawność językowa'] = f"{correctness_score}/2 - {correctness_feedback}"

    # ✅ Podsumowanie wszystkich kryteriów oceny
    final_score = correctness_score  # Można dodać inne kryteria, jeśli chcesz pełne 10 pkt
    feedback['📌 **Podsumowanie oceny:**'] = f"🔹 **Łączny wynik**: {final_score}/2 pkt\n\n" + \
        "🔹 **Kryteria oceny:**\n" + \
        "• Treść: 0-4 pkt (czy spełnia wszystkie podpunkty?)\n" + \
        "• Spójność i logika: 0-2 pkt (czy tekst jest logiczny i dobrze zorganizowany?)\n" + \
        "• Zakres środków językowych: 0-2 pkt (czy używane są różnorodne słowa?)\n" + \
        "• Poprawność środków językowych: 0-2 pkt (czy tekst ma błędy ortograficzne i gramatyczne?)"

    return feedback, errors_table, highlighted_text

# ✅ Interfejs użytkownika
st.title("📩 Automatyczna ocena pisemnych wypowiedzi")
st.write("✏️ Wybierz typ tekstu i sprawdź, czy spełnia kryteria egzaminacyjne.")

selected_format = st.radio("Wybierz format tekstu:", ("E-mail", "Blog"))
email_text = st.text_area("📌 Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        result, errors_table, highlighted_text = evaluate_email(email_text, selected_format)

        for key, value in result.items():
            st.write(f"**{key}:** {value}")

        if errors_table is not None and not errors_table.empty:
            st.write("### ❌ Lista błędów i poprawek:")
            st.dataframe(errors_table, height=300, width=700)

        # ✅ Wyświetlamy tekst z zaznaczonymi błędami
        st.write("### 🔍 Tekst z zaznaczonymi błędami:")
        st.markdown(f"<p style='font-size:16px;'>{highlighted_text}</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Wpisz treść przed sprawdzeniem.")
