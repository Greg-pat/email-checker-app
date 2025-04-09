import streamlit as st
import language_tool_python
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

# Konfiguracja strony
st.set_page_config(page_title="Ocena wypowiedzi pisemnej", layout="centered")
st.title("Automatyczna ocena wypowiedzi pisemnej")
st.markdown(f"**Data:** {datetime.now().strftime('%Y-%m-%d')}")

# Narzędzie do sprawdzania języka
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# Lista dostępnych tematów
TEMATY = {
    "Opisz swoje ostatnie wakacje": ["holiday", "trip", "beach", "mountains", "memories", "visited", "hotel"],
    "Napisz o swoich planach na najbliższy weekend": ["weekend", "going to", "plan", "cinema", "friends", "family"],
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": ["meet", "visit", "place", "Poland", "invite", "schedule"],
    "Opisz swój udział w szkolnym przedstawieniu": ["school play", "role", "stage", "acting", "performance", "nervous"],
    "Podziel się wrażeniami z wydarzenia szkolnego": ["event", "competition", "school", "experience", "memorable"],
    "Opisz swoje nowe hobby": ["hobby", "started", "enjoy", "benefits", "passion"],
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną": ["online learning", "advantages", "disadvantages", "difficult"],
    "Opisz szkolną wycieczkę, na której byłeś": ["school trip", "visited", "museum", "amazing", "historical"],
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": ["sightseeing", "places", "Poland", "tour", "recommend"]
}

# Wybór tematu
selected_temat = st.selectbox("Wybierz temat wypowiedzi:", list(TEMATY.keys()))

# Wprowadzenie tekstu
email_text = st.text_area("Wpisz swoją wypowiedź:", height=250)

# Przycisk sprawdzania
if st.button("Sprawdź"):
    if len(email_text.split()) < 10:
        st.warning("✋ Wpisz co najmniej 10 słów, aby uruchomić ocenę.")
    else:
        matches = tool.check(email_text)
        błędy = []
        tekst_zaznaczony = email_text
        przesunięcie = 0

        for m in matches:
            start = m.offset + przesunięcie
            end = m.offset + m.errorLength + przesunięcie
            błędny_fragment = tekst_zaznaczony[start:end]
            poprawka = f"<span style='color:red; font-weight:bold; text-decoration:underline'>{błędny_fragment}</span>"
            tekst_zaznaczony = tekst_zaznaczony[:start] + poprawka + tekst_zaznaczony[end:]
            przesunięcie += len(poprawka) - len(błędny_fragment)
            błędy.append({
                "Błąd": email_text[m.offset:m.offset + m.errorLength],
                "Poprawna forma": ', '.join(m.replacements) if m.replacements else "-",
                "Typ błędu": m.ruleIssueType
            })

        df_błędów = pd.DataFrame(błędy)

        słowa = email_text.lower().split()
        liczba_słów = len(słowa)
        punkty_słowa = 2 if 50 <= liczba_słów <= 120 else 1 if 30 <= liczba_słów < 50 or liczba_słów > 120 else 0
        punkty_komentarz = "✅ Liczba słów: {0} - Zgodna z wymaganym zakresem (50–120).".format(liczba_słów) if punkty_słowa == 2 else "⚠️ Liczba słów: {0} - Poza wymaganym zakresem 50–120 słów.".format(liczba_słów)

        zgodność = sum(1 for słowo in TEMATY[selected_temat] if słowo in słowa)
        punkty_treść = 4 if zgodność >= 3 else 3 if zgodność == 2 else 2 if zgodność == 1 else 1
        punkty_spójność = 2 if any(x in email_text for x in ["and", "but", "because", "however"]) else 1
        punkty_zakres = 2 if any(x in email_text for x in ["amazing", "delicious", "fantastic", "unforgettable"]) else 1
        punkty_poprawność = 2 if len(błędy) == 0 else 1 if len(błędy) < 5 else 0

        suma = min(10, punkty_słowa + punkty_treść + punkty_spójność + punkty_zakres + punkty_poprawność)

        st.subheader("📊 Wyniki oceny:")
        st.markdown(f"📄 **Zgodna ilość słów**: {punkty_słowa}/2 - {punkty_komentarz}")
        st.markdown(f"📝 **Treść**: {punkty_treść}/4 - Zgodność z tematem.")
        st.markdown(f"🔗 **Spójność i logika**: {punkty_spójność}/2")
        st.markdown(f"📖 **Zakres środków językowych**: {punkty_zakres}/2")
        st.markdown(f"✅ **Poprawność językowa**: {punkty_poprawność}/2")
        st.markdown(f"📌 **Łączny wynik**: **{suma}/10 pkt**")

        if not df_błędów.empty:
            st.subheader("❌ Lista błędów i poprawek:")
            st.dataframe(df_błędów, use_container_width=True)

        st.subheader("🔍 Tekst z zaznaczonymi błędami:")
        st.markdown(f"<div style='font-size:16px'>{tekst_zaznaczony}</div>", unsafe_allow_html=True)

        # Propozycja lepszej wersji
        st.subheader("💡 Propozycja poprawionej wersji tekstu:")
        poprawiony = tool.correct(email_text)
        st.text_area("Poprawiony tekst (propozycja):", value=poprawiony, height=200)
