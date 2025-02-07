import streamlit as st
from textblob import TextBlob
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-US')
spell = SpellChecker(language='en')

# ✅ Lista słów ignorowanych przez spellchecker (bo nie są błędami)
IGNORE_WORDS = {
    "job", "you", "week", "news", "years", "media", "trends", "concerned", 
    "for", "position", "creative", "experience", "application", "manager", 
    "changes", "employer", "sir/madam", "references"
}

# ✅ Funkcja do usuwania znaków interpunkcyjnych na końcu wyrazu
def clean_word(word):
    return re.sub(r'[^\w\s]', '', word)

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
        correction = match.replacements[0] if match.replacements else "Nie znaleziono poprawnej formy"

        # ✅ Filtrujemy fałszywe błędy
        if clean_word(error.lower()) in IGNORE_WORDS or len(error) < 2:
            continue  

        grammar_errors[error] = (correction, "Błąd gramatyczny")
        corrected_text = re.sub(rf'\b{re.escape(error)}\b', f"<span style='color:red; font-weight:bold;'>{error}</span>", corrected_text, 1)

    # ✅ Wykrywanie błędów ortograficznych (pyspellchecker)
    misspelled_words = spell.unknown([clean_word(w) for w in email_text.split()])
    for word in misspelled_words:
        if clean_word(word.lower()) in IGNORE_WORDS:
            continue  # Ignorujemy poprawne słowa

        correction = spell.correction(word) or "Nie znaleziono poprawnej formy"
        spell_errors[word] = (correction, "Błąd ortograficzny")
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
                    columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
                )

                # ✅ Wyświetlamy tabelę
                st.dataframe(errors_table, height=300, width=700)

            else:
                st.write(f"**{key}:** {value}")
    else:
        st.warning("⚠️ Wpisz treść maila przed sprawdzeniem.")
