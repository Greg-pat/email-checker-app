import streamlit as st
import nltk
from textblob import TextBlob
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.data import find

# Pobranie zasobów wymaganych przez NLTK
nltk.download('punkt')
import streamlit as st
import nltk
from textblob import TextBlob
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download('punkt')

def evaluate_email(email_text, task_requirements):
    feedback = {}

    # Ocena treści
    missing_points = [point for point in task_requirements if point.lower() not in email_text.lower()]
    if missing_points:
        feedback['Treść'] = f'Nie uwzględniono: {", ".join(missing_points)}.'
    else:
        feedback['Treść'] = 'Wszystkie punkty zostały uwzględnione.'

    # Spójność i logika
    sentences = sent_tokenize(email_text)
    feedback['Spójność'] = 'Tekst jest spójny.' if len(sentences) >= 3 else 'Tekst jest za krótki.'

    # Zakres środków językowych
    words = word_tokenize(email_text)
    unique_words = set(words)
    feedback['Zakres językowy'] = 'Słownictwo jest zróżnicowane.' if len(unique_words) > len(words) * 0.6 else 'Zbyt powtarzalne słownictwo.'

    # Poprawność językowa
    blob = TextBlob(email_text)
    errors = [str(correction) for word, correction in blob.correct().words if word != correction]
    feedback['Poprawność'] = f'Popraw możliwe błędy: {", ".join(errors)}.' if errors else 'Brak oczywistych błędów.'

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
