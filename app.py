import streamlit as st
from textblob import TextBlob
import language_tool_python
import pandas as pd

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')

# ✅ Nowa funkcja analizy treści
def check_content(email_text, required_points):
    missing_points = []
    email_text_lower = email_text.lower()

    for point in required_points:
        words = point.split()  # Rozbijamy frazę na słowa
        found = all(word in email_text_lower for word in words)  # Sprawdzamy, czy wszystkie są w tekście
        if not found:
            missing_points.append(point)

    return missing_points

# ✅ Nowa funkcja oceny e-maila
def evaluate_email(email_text, task_requirements):
    feedback = {}

    # ✅ Nowa ocena treści
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

    # ✅ Poprawność językowa – usunięcie powtarzających się błędów
    matches = tool.check(email_text)
    grammar_errors = {}
    for match in matches:
        error = match.context[match.offset:match.offset + match.errorLength]
        correction = match.replacements[0] if match.replacements else "Brak propozycji"
        if error not in grammar_errors:
            grammar_errors[error] = (correction, match.message)

    feedback['Poprawność'] = grammar_errors if grammar_errors else 'Brak oczywistych błędów.'

    return feedback

st.title("📩 Sprawdzanie maili na egzamin ósmoklasisty")
st.write("✏️ Wpisz swój e-mail i sprawdź, czy spełnia kryteria egzaminacyjne.")

task = ['poinformować o terminie', 'zaprosić na wydarzenie', 'zapytać o szczegóły']

email_text = st.text_area("📌 Wpisz swój e-mail tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        result = evaluate_email(email_text, task)

        # ✅ Wyświetlanie wyników w czytelnej formie
        for key, value in result.items():
            if key == "Poprawność" and isinstance(value, dict):
                st.write(f"**{key}:**")
                
                # ✅ Tworzymy tabelę z błędami
                errors_table = pd.DataFrame(
                    [(error, correction, message) for error, (correction, message) in value.items()],
                    columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Wyjaśnienie"]
                )

                # ✅ Wyświetlamy tabelę
                st.dataframe(errors_table)

            else:
                st.write(f"**{key}:** {value}")
    else:
        st.warning("⚠️ Wpisz treść maila przed sprawdzeniem.")
