import streamlit as st
from textblob import TextBlob
import language_tool_python

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')

# ✅ Funkcja oceny e-maila
def evaluate_email(email_text, task_requirements):
    feedback = {}

    # Ocena treści
    missing_points = [point for point in task_requirements if point.lower() not in email_text.lower()]
    if missing_points:
        feedback['Treść'] = f'Nie uwzględniono: {", ".join(missing_points)}.'
    else:
        feedback['Treść'] = 'Wszystkie punkty zostały uwzględnione.'

    # ✅ Spójność i długość tekstu
    sentences = email_text.split('.')
    feedback['Spójność'] = 'Tekst jest spójny.' if len(sentences) >= 3 else 'Tekst jest za krótki.'

    # Zakres środków językowych
    words = email_text.split()
    unique_words = set(words)
    feedback['Zakres językowy'] = 'Słownictwo jest zróżnicowane.' if len(unique_words) > len(words) * 0.6 else 'Zbyt powtarzalne słownictwo.'

    # ✅ Poprawność językowa (gramatyka i ortografia)
    matches = tool.check(email_text)
    grammar_errors = [match.ruleId for match in matches]
    feedback['Poprawność'] = f'Znalezione błędy: {", ".join(grammar_errors)}.' if grammar_errors else 'Brak oczywistych błędów.'

    return feedback

st.title("Sprawdzanie maili na egzamin ósmoklasisty")
st.write("Wpisz swój e-mail i sprawdź, czy spełnia kryteria egzaminacyjne.")

task = ['poinformować o terminie', 'zaprosić na wydarzenie', 'zapytać o szczegóły']

email_text = st.text_area("Wpisz swój email tutaj:")

if st.button("Sprawdź"):
    if email_text:
        result = evaluate_email(email_text, task)
        for key, value in result.items():
            st.write(f"**{key}:** {value}")
    else:
        st.warning("Wpisz treść maila przed sprawdzeniem.")
