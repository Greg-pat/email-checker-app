import streamlit as st
import language_tool_python
import pandas as pd

# ✅ Inicjalizacja narzędzia do sprawdzania błędów
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# ✅ Tematy egzaminacyjne i słowa kluczowe
TEMATY = {
    "Opisz swoje ostatnie wakacje": ["holiday", "trip", "beach", "mountains", "memories", "visited", "hotel"],
    "Napisz o swoich planach na najbliższy weekend": ["weekend", "going to", "plan", "cinema", "friends", "family"],
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": ["meet", "visit", "place", "Poland", "invite", "schedule"],
    "Opisz swój udział w szkolnym przedstawieniu": ["school play", "role", "stage", "acting", "performance", "nervous"],
    "Podziel się wrażeniami z wydarzenia szkolnego": ["event", "competition", "school", "experience", "memorable"],
    "Opisz swoje nowe hobby": ["hobby", "started", "enjoy", "benefits", "passion"],
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną": ["online learning", "advantages", "disadvantages", "difficult"],
    "Opisz szkolną wycieczkę, na której byłeś": ["school trip", "visited", "museum", "amazing", "historical"],
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": ["sightseeing", "places", "Poland", "tour", "recommend"],
}

# ✅ Przykładowe idealne wypowiedzi
PRZYKLADY = {
    "Opisz swoje ostatnie wakacje": 
        "Last summer, I went to the mountains with my family. We hiked every day and stayed in a small wooden cabin.",
    "Napisz o swoich planach na najbliższy weekend":
        "This weekend, I’m going to visit my grandparents. We will bake a cake and go for a walk in the park.",
    "Zaproponuj spotkanie koledze/koleżance z zagranicy":
        "Would you like to meet in Warsaw next Saturday? I can show you the Old Town and we can eat Polish dumplings.",
    "Opisz swój udział w szkolnym przedstawieniu":
        "I played the role of a prince in our school play. I was very nervous at first, but in the end it was a lot of fun!",
    "Podziel się wrażeniami z wydarzenia szkolnego":
        "Last month, I took part in a school quiz competition. It was exciting and I learned many new facts!",
    "Opisz swoje nowe hobby":
        "Recently, I started learning how to play the guitar. It’s difficult, but I love playing my favourite songs.",
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną":
        "During online learning, I missed seeing my friends. However, I enjoyed having more time to sleep.",
    "Opisz szkolną wycieczkę, na której byłeś":
        "We went on a school trip to Kraków last spring. I really liked visiting Wawel Castle and the Old Town.",
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce":
        "Let’s visit Gdańsk together! It’s a beautiful city by the sea and has many interesting museums."
}

# ✅ Sprawdzanie poprawności językowej
def ocena_poprawności(tekst):
    try:
        matches = tool.check(tekst)
    except Exception:
        return 0, None, tekst

    błędy = []
    tekst_zaznaczony = tekst
    for match in matches:
        start = match.offset
        end = start + match.errorLength
        błąd = tekst[start:end].strip()
        poprawka = match.replacements[0] if match.replacements else "Brak propozycji"
        if not błąd:
            continue
        tekst_zaznaczony = tekst_zaznaczony.replace(błąd, f"**:red[{błąd}]**", 1)
        błędy.append((błąd, poprawka, "Błąd gramatyczny"))

    tabela_błędów = pd.DataFrame(
        błędy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if błędy else None

    return 2 if len(błędy) == 0 else 1 if len(błędy) < 5 else 0, tabela_błędów, tekst_zaznaczony

# ✅ Ocena treści
def ocena_treści(tekst, temat):
    if temat not in TEMATY:
        return 0, "Nie wybrano tematu lub temat nieobsługiwany."
    słowa_kluczowe = TEMATY[temat]
    liczba_wystąpień = sum(1 for słowo in słowa_kluczowe if słowo.lower() in tekst.lower())
    if liczba_wystąpień >= 5:
        return 4, "Treść w pełni zgodna z tematem. Świetnie!"
    elif liczba_wystąpień >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif liczba_wystąpień >= 2:
        return 2, "Częściowa zgodność, rozwinięcie tematu jest niewystarczające."
    return 1 if liczba_wystąpień == 1 else 0, "Treść nie jest zgodna z tematem."

# ✅ Spójność i logika
def ocena_spójności(tekst):
    if any(s in tekst.lower() for s in ["however", "therefore", "firstly", "in conclusion"]):
        return 2, "Tekst jest dobrze zorganizowany."
    return 1, "Spójność może być lepsza – użyj więcej wyrażeń łączących."

# ✅ Zakres słownictwa
def ocena_zakresu(tekst):
    unikalne_słowa = set(tekst.lower().split())
    if len(unikalne_słowa) > 40:
        return 2, "Bardzo bogate słownictwo!"
    return 1 if len(unikalne_słowa) > 20 else 0, "Słownictwo jest zbyt proste."

# ✅ Liczba słów
def ocena_długości(tekst):
    liczba = len(tekst.split())
    if 50 <= liczba <= 120:
        return 2, f"Liczba słów: {liczba} - Poprawna długość."
    return 1 if liczba > 30 else 0, f"Liczba słów: {liczba} - poza zakresem."

# ✅ Główna funkcja oceny
def ocena_tekstu(tekst, temat):
    pkt_treść, op_treść = ocena_treści(tekst, temat)
    pkt_spójn, op_spójn = ocena_spójności(tekst)
    pkt_zakres, op_zakres = ocena_zakresu(tekst)
    pkt_popraw, tabela_błędów, tekst_zazn = ocena_poprawności(tekst)
    pkt_dł, op_dł = ocena_długości(tekst)

    suma = min(pkt_treść + pkt_spójn + pkt_zakres + pkt_popraw + pkt_dł, 10)

    rekomendacje = []
    if pkt_treść < 4: rekomendacje.append("📌 **Treść**: Dodaj więcej szczegółów i rozwiń swoje pomysły.")
    if pkt_spójn < 2: rekomendacje.append("📌 **Spójność**: Użyj więcej wyrażeń łączących, np. *however, therefore*.")
    if pkt_zakres < 2: rekomendacje.append("📌 **Zakres**: Użyj bardziej różnorodnych słów.")
    if pkt_popraw < 2: rekomendacje.append("📌 **Poprawność**: Sprawdź błędy gramatyczne i ortograficzne.")

    wyniki = {
        "📝 Treść": f"{pkt_treść}/4 - {op_treść}",
        "🔗 Spójność": f"{pkt_spójn}/2 - {op_spójn}",
        "📖 Zakres": f"{pkt_zakres}/2 - {op_zakres}",
        "✅ Poprawność": f"{pkt_popraw}/2 - Im mniej błędów, tym lepiej!",
        "📏 Długość": f"{pkt_dł}/2 - {op_dł}",
        "📌 Łączny wynik:": f"🔸 {suma}/10 pkt"
    }

    return wyniki, tabela_błędów, tekst_zazn

# ✅ UI Streamlit
st.set_page_config("Automatyczna ocena", layout="centered")
st.title("📩 Automatyczna ocena wypowiedzi pisemnej")
selected_temat = st.selectbox("📌 Wybierz temat:", list(TEMATY.keys()))
tekst = st.text_area("✍️ Wpisz swoją wypowiedź (50–120 słów):", height=200)

if st.button("✅ Sprawdź"):
    wyniki, tabela, tekst_zazn = ocena_tekstu(tekst, selected_temat)

    st.markdown("## 📊 Wyniki oceny:")
    for k, v in wyniki.items():
        st.markdown(f"**{k}** {v}")

    if tabela is not None:
        st.markdown("### ❌ Lista błędów i poprawek:")
        st.dataframe(tabela, use_container_width=True)

    st.markdown("### 📝 Tekst z zaznaczonymi błędami:")
    st.markdown(tekst_zazn, unsafe_allow_html=True)

    st.markdown("### 🟦 Przykład idealnej wypowiedzi:")
    st.info(PRZYKLADY[selected_temat])
