import streamlit as st
import language_tool_python
import pandas as pd
from datetime import date

# Konfiguracja strony
st.set_page_config(page_title="Ocena pisemnych wypowiedzi", layout="centered")
st.title("\U0001F4E9 Automatyczna ocena wypowiedzi pisemnej")
st.write(f"**Data:** {date.today()}")

# Narzędzie do sprawdzania błędów językowych
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# Tematy egzaminacyjne
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

# Ocena poprawności językowej

def ocena_poprawności(tekst):
    matches = tool.check(tekst)
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

    tabela_błędów = pd.DataFrame(błędy, columns=["Błąd", "Poprawna forma", "Typ błędu"]) if błędy else None
    pkt = 2 if len(błędy) == 0 else 1 if len(błędy) < 5 else 0
    return pkt, tabela_błędów, tekst_zaznaczony

# Ocena treści

def ocena_treści(tekst, temat):
    słowa_kluczowe = TEMATY.get(temat, [])
    liczba = sum(1 for s in słowa_kluczowe if s in tekst.lower())
    if liczba >= 5:
        return 4, "Treść w pełni zgodna z tematem. Świetnie!"
    elif liczba >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif liczba >= 2:
        return 2, "Częściowa zgodność."
    elif liczba == 1:
        return 1, "Tylko minimalna zgodność z tematem."
    return 0, "Treść nie jest zgodna z tematem."

# Ocena spójności

def ocena_spójności(tekst):
    if any(x in tekst.lower() for x in ["however", "therefore", "finally", "in conclusion"]):
        return 2, "Tekst dobrze zorganizowany."
    return 1, "Brakuje spójności logicznej."

# Zakres językowy

def ocena_zakresu(tekst):
    wyrazy = set(tekst.lower().split())
    if len(wyrazy) > 40:
        return 2, "Bogate słownictwo."
    elif len(wyrazy) > 20:
        return 1, "Słownictwo umiarkowane."
    return 0, "Słownictwo bardzo ubogie."

# Długość

def ocena_dlugosci(tekst):
    liczba = len(tekst.split())
    if 50 <= liczba <= 120:
        return 2, f"Liczba słów: {liczba} - Poprawna długość."
    return 1, f"Liczba słów: {liczba} - poza zakresem."

# Ocena całościowa

def ocena_tekstu(tekst, temat):
    t, ot = ocena_treści(tekst, temat)
    s, os = ocena_spójności(tekst)
    z, oz = ocena_zakresu(tekst)
    p, tabela, zaznaczony = ocena_poprawności(tekst)
    d, od = ocena_dlugosci(tekst)
    suma = t + s + z + p + d
    suma = min(suma, 10)
    return t, s, z, p, d, suma, ot, os, oz, od, tabela, zaznaczony

# UI
selected_temat = st.selectbox("Wybierz temat wypowiedzi:", list(TEMATY.keys()))
tekst = st.text_area("Wpisz swój tekst:")
if st.button("Sprawdź"):
    if tekst:
        t, s, z, p, d, suma, ot, os, oz, od, tabela, zaznaczony = ocena_tekstu(tekst, selected_temat)

        st.markdown("## \U0001F4CA Wyniki oceny:")
        st.markdown(f"**Treść:** {t}/4 - {ot}")
        st.markdown(f"**Spójność:** {s}/2 - {os}")
        st.markdown(f"**Zakres:** {z}/2 - {oz}")
        st.markdown(f"**Poprawność:** {p}/2 - Im mniej błędów, tym lepiej!")
        st.markdown(f"**Długość:** {d}/2 - {od}")
        st.markdown(f"### \U0001F4CC Łączny wynik: **{suma}/10 pkt**")

        if tabela is not None:
            st.markdown("### ❌ Lista błędów i poprawek:")
            st.dataframe(tabela, use_container_width=True)

        st.markdown("### \U0001F4DD Tekst z zaznaczonymi błędami:")
        st.markdown(zaznaczony, unsafe_allow_html=True)
