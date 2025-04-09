import streamlit as st
import language_tool_python
import pandas as pd
from datetime import datetime

# Konfiguracja strony
st.set_page_config(page_title="Ocena wypowiedzi pisemnej", layout="centered")
st.title("📧 Automatyczna ocena wypowiedzi pisemnej")
st.markdown(f"**Data:** {datetime.now().strftime('%Y-%m-%d')}")

# Lista tematów i słów kluczowych
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
temat = st.selectbox("Wybierz temat swojej wypowiedzi:", list(TEMATY.keys()))

# Pole do wpisania tekstu
tekst = st.text_area("Wpisz swoją wypowiedź:", height=250)

# Przycisk do uruchomienia sprawdzania
if st.button("Sprawdź"):
    tool = language_tool_python.LanguageTool('en-GB')
    matches = tool.check(tekst)

    # Podkreślanie błędów
    błędy = []
    tekst_zaznaczony = tekst
    przesunięcie = 0
    for m in matches:
        start = m.offset + przesunięcie
        end = m.offset + m.errorLength + przesunięcie
        błędny_fragment = tekst_zaznaczony[start:end]
        poprawka = f"<span style='color:red; font-weight:bold; text-decoration:underline'>{błędny_fragment}</span>"
        tekst_zaznaczony = tekst_zaznaczony[:start] + poprawka + tekst_zaznaczony[end:]
        przesunięcie += len(poprawka) - len(błędny_fragment)
        błędy.append({
            "Błąd": m.context.text[m.context.offset:m.context.offset + m.context.length],
            "Poprawna forma": ', '.join(m.replacements) if m.replacements else "-",
            "Typ błędu": m.ruleIssueType
        })

    # Ocena długości tekstu
    liczba_słów = len(tekst.split())
    punkty_słowa = 2 if 50 <= liczba_słów <= 120 else 1 if 30 <= liczba_słów < 50 or liczba_słów > 120 else 0

    # Ocena treści względem tematu
    słowa = tekst.lower().split()
    zgodność = sum(1 for słowo in TEMATY[temat] if słowo in słowa)
    punkty_treść = 4 if zgodność >= 3 else 3 if zgodność == 2 else 2 if zgodność == 1 else 1

    # Ocena spójności
    punkty_spójność = 2 if any(x in tekst for x in ["and", "but", "because", "however", "then", "after that"]) else 1

    # Zakres słownictwa
    punkty_zakres = 2 if any(x in tekst for x in ["amazing", "delicious", "fantastic", "unforgettable", "brilliant", "creative"]) else 1

    # Poprawność językowa
    punkty_poprawność = 2 if len(matches) == 0 else 1 if len(matches) < 5 else 0

    suma = min(10, punkty_słowa + punkty_treść + punkty_spójność + punkty_zakres + punkty_poprawność)

    # Wyświetlanie wyników
    st.subheader("📊 Wyniki oceny:")
    st.markdown(f"📄 **Zgodna ilość słów**: {punkty_słowa}/2 - {'✅ Poprawna długość.' if punkty_słowa == 2 else '⚠️ Liczba słów poza zakresem 50–120.'}")
    st.markdown(f"📝 **Treść**: {punkty_treść}/4 - {'Treść zgodna z tematem' if punkty_treść >= 3 else 'Spróbuj lepiej dopasować treść do tematu.'}")
    st.markdown(f"🔗 **Spójność i logika**: {punkty_spójność}/2")
    st.markdown(f"📖 **Zakres językowy**: {punkty_zakres}/2")
    st.markdown(f"✅ **Poprawność językowa**: {punkty_poprawność}/2")
    st.markdown(f"📌 **Łączny wynik**: **{suma}/10 pkt**")

    if błędy:
        st.subheader("❌ Lista błędów i poprawek:")
        st.dataframe(pd.DataFrame(błędy))

    st.subheader("🔍 Tekst z zaznaczonymi błędami:")
    st.markdown(f"<div style='font-size:16px'>{tekst_zaznaczony}</div>", unsafe_allow_html=True)

    st.subheader("💡 Propozycja poprawionej wersji tekstu:")
    st.text_area("Poprawiony tekst (propozycja):", value=tool.correct(tekst), height=200)
