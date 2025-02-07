import streamlit as st
from textblob import TextBlob
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')
spell = SpellChecker(language='en')

# ✅ Nowa funkcja analizy treści
def check_content(email_text, required_points):
    missing_points = []
    email_text_lower = email_text.lower()

    synonyms = {
        "poinformować o terminie": ["inform about the date", "notify about the time", "mention the date"],
        "zaprosić na wydarzenie": ["invite to the event", "send an invitation", "ask to join"],
        "zapytać o szczegóły": ["ask for details", "inquire about", "request further information", "look forward to hearing"]
    }

    for point, variations in synonyms.items():
        found = any(variation in email_text_lower for variation in variations)
        if not found:
            missing_points.append(point)

    return missing_points

# ✅ Nowa funkcja oceny e-maila
def evaluate_email(email_text, task_requirements):
    feedback = {}

    # ✅ Ocena treści
    missing_points = check_content(email_text, task_requirements)
    if missing_points:
        feedback['Treść'] = f'Nie uwzględniono: {", ".join(missing_points)}.'
    else:
        feedback['Treść'] = 'Wszystkie punkty zostały uwzględnione.'

    # ✅ Spójność tekstu
    sentences = email_text.split('.')
    feedback['Spójność'] = 'Tekst jest spójny.' if len(sentences) >= 3 else 'Tekst jest za krótki.'

    # ✅ Zakres środków językowych
    words = email_text.split()
    unique_words = set(words)
    feedback['Zakres językowy'] = 'Słownictwo jest zróżnicowane.' if len(unique_words) > len(words) * 0.6 else 'Zbyt powtarzalne słownictwo.'

    # ✅ Poprawność językowa
    matches = tool.check(email_text)
    grammar_errors = {}
    spell_errors = {}
    corrected_text = email_text

    # ✅ Wykrywanie błędów gramatycznych (LanguageTool)
    for match in matches:
        error = match.context[match.offset:match.offset + match.errorLength]
        correction = match.replacements[0] if match.replacements else "Brak propozycji"
        if error not in grammar_errors:
            grammar_errors[error] = (correction, match.message)
            corrected_text = re.sub(rf'\b{re.escape(error)}\b', f"<span style='color:red; font-weight:bold;'>{error}</span>", corrected_text, 1)

    # ✅ Wykrywanie błędów ortograficznych (pyspellchecker)
    misspelled_words = spell.unknown(email_text.split())
    for word in misspelled_words:
        correction = spell.correction(word) or "Brak propozycji"
        if word not in grammar_errors:
            spell_errors[word] = (correction, "Prawdopodobny błąd ortograficzny")
            corrected_text = re.sub(rf'\b{re.escape(word)}\b', f"<span style='color:red; font-weight:bold;'>{word}</span>", corrected_text, 1)

    # ✅ Połączenie błędów gramatycznych i ortograficznych
    all_errors = {**grammar_errors, **spell_errors}
    feedback['Poprawność'] = all_errors if all_errors else 'Brak oczywistych błędów.'

    return feedback, corrected_text

st.title("📩 Sprawdzanie maili na egzamin ósmoklasisty")
st.write("✏️ Wpisz swój e-mail i sprawdź, czy spełnia kryteria egzaminacyjne.")

task = ['poinformować o terminie', 'zaprosić na wydarzenie', 'zapytać o szczegóły']

email_text = st.text_area("📌 Wpisz swój e-mail tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        result, highlighted_text = evaluate_email(email_text, task)

        # ✅ Wyświetlamy tekst z zaznaczonymi błędami na czerwono
        st.write("### 🔍 Tekst z zaznaczonymi błędami:")
        st.markdown(f"<p style='font-size:16px;'>{highlighted_text}</p>", unsafe_allow_html=True)

        # ✅ Wyświetlanie wyników
        for key, value in result.items():
            if key == "Poprawność" and isinstance(value, dict):
                st.write(f"**{key}:**")
                
                # ✅ Tworzymy tabelę z błędami i poprawkami
                errors_table = pd.DataFrame(
                    [(error, correction, message) for error, (correction, message) in value.items()],
                    columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Wyjaśnienie"]
                )

                # ✅ Wyświetlamy tabelę
                st.dataframe(errors_table, height=300, width=700)

            else:
                st.write(f"**{key}:** {value}")
    else:
        st.warning("⚠️ Wpisz treść maila przed sprawdzeniem.")
