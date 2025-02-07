import os
import streamlit as st
import spacy
from textblob import TextBlob
import subprocess

# ✅ Pobieramy model języka angielskiego jeśli go nie ma
model_name = "en_core_web_sm"
try:
    nlp = spacy.load(model_name)
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", model_name])
    nlp = spacy.load(model_name)

# ✅ Funkcja oceny e-maila
def evaluate_email(email_text, task_requirements):
    feedback = {}

    # Ocena treści
    missing_points = [point for point in task_requirements if point.lower() not in email_text.lower()]
    if missing_points:
        feedback['Treść'] = f'Nie uwzględniono: {", ".join(missing_points)}.'
    else:
        feedback['Treść'] = 'Wszystkie punkty zostały uwzględnione.'

    # ✅ Spójność i logika (liczba zdań)
    doc = nlp(email_text)
    sentences = list(doc.sents)
    feedback['Spójność'] = 'Tekst jest spójny.' if len(sentences) >= 3 else 'Tekst jest za krótki.'

    # Zakres środków językowych
    unique_words = set([token.text.lower() for token in doc if token.is_alpha])
    feedback['Zakres językowy'] = 'Słownictwo jest zróżnicowane.' if len(unique_words) > len(doc) * 0.6 else 'Zbyt powtarzalne słownictwo.'

    # Poprawność językowa (gramatyka i ortografia)
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
