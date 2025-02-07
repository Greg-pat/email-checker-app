import streamlit as st
from textblob import TextBlob
import language_tool_python
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')

# ✅ Nowa funkcja analizy treści z synonimami i frazami kontekstowymi
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

    # ✅ Poprawiona ocena treści z synonimami
    missing_points = check_content(email_text, task_requirements)
    if missing_points:
        feedback['Treść'] = f'Nie uwzględniono: {", ".join(missing_points)}.'
    else:
        feedback['Treść'] = 'Wszystkie punkty zostały uwzględnione.'

    # ✅ Spójność i długość tekstu
    sentences = email_text.split('.')
    feedback['Spójność'] = 'Tekst jest spójny.' if len(sentences) >= 3 else 'Tekst jest za krótki.'

    # ✅ Zakres środków językowych
    words = email_text.split()
    unique_words = set(words)
    feedback['Zakres językowy'] = 'Słownictwo jest zróżnicowane.' if len(unique_words) > len(words) * 0.6 else 'Zbyt powtarzalne słownictwo.'

    # ✅ Poprawność językowa – dokładniejsze poprawki i przykłady
    matches = tool.check(email_text)
    grammar_errors = {}
    corrected_text = email_text

    for match in matches:
        error = match.context[match.offset:match.offset + match.errorLength]
        correction = match.replacements[0] if match.replacements else "Brak propozycji"

        if error not in grammar_errors:
            grammar_errors[error] = (correction, match.message, email_text.replace(error, correction))

            # ✅ Podkreślenie błędu w tekście
            corrected_text = re.sub(rf'\b{re.escape(error)}\b', f"**{error}**", corrected_text, 1)

    feedback['Poprawność'] = grammar_errors if grammar_errors else 'Brak oczywistych błędów.'

    return feedback, corrected_text

st.title("📩 Sprawdzanie maili na egzamin ósmoklasisty")
st.write("✏️ Wpisz swój e-mail i sprawdź, czy spełnia kryteria egzaminacyjne.")

task = ['poinformować o terminie', 'zaprosić na wydarzenie', 'zapytać o szczegóły']

email_text = st.text_area("📌 Wpisz swój e-mail tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        result, highlighted_text = evaluate_email(email_text, task)

        # ✅ Wyświetlamy tekst z podkreślonymi błędami
        st.write("### 🔍 Tekst z podkreślonymi błędami:")
        st.markdown(f"**{highlighted_text}**")

        # ✅ Wyświetlanie wyników
        for key, value in result.items():
            if key == "Poprawność" and isinstance(value, dict):
                st.write(f"**{key}:**")
                
                # ✅ Tworzymy tabelę z błędami i poprawkami
                errors_table = pd.DataFrame(
                    [(error, correction, message, sentence) for error, (correction, message, sentence) in value.items()],
                    columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Wyjaśnienie", "✅ Przykładowe poprawione zdanie"]
                )

                # ✅ Wyświetlamy tabelę
                st.dataframe(errors_table, height=300, width=700)

            else:
                st.write(f"**{key}:** {value}")
    else:
        st.warning("⚠️ Wpisz treść maila przed sprawdzeniem.")
