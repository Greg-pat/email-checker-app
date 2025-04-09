import streamlit as st
import pandas as pd
import language_tool_python

# Inicjalizacja narzędzia do sprawdzania gramatyki
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# Tematy i słowa kluczowe
TEMATY = {
    "Opisz swoje ostatnie wakacje": ["holiday", "trip", "beach", "mountains", "memories", "visited", "hotel"],
    "Napisz o swoich planach na najbliższy weekend": ["weekend", "going to", "plan", "cinema", "friends", "family"],
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": ["meet", "visit", "place", "Poland", "invite", "schedule"],
    "Opisz swój udział w szkolnym przedstawieniu": ["school play", "role", "stage", "acting", "performance", "nervous"],
    "Podziel się wrażeniami z wydarzenia szkolnego": ["event", "competition", "school", "experience", "memorable"],
}

# Przykłady wypowiedzi
PRZYKLADY = {
    "Opisz swoje ostatnie wakacje": "Last summer, I went to the mountains with my family. We hiked every day and stayed in a small wooden cabin. One day, we saw a deer and took a lot of pictures. I really enjoyed spending time in nature and eating local food. The weather was great and I felt relaxed. I hope to go back there next year!",
    "Napisz o swoich planach na najbliższy weekend": "This weekend, I’m planning to visit my grandparents in the countryside. We will bake cookies together and walk in the forest. I also want to read a new book and watch a film with my family. On Sunday, we’ll go to church and have a big lunch. I love weekends like this because they help me rest.",
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": "Hi! I’m so excited that you’re coming to Poland next week! I would love to meet you in Warsaw on Saturday. We can visit the Old Town, try pierogi and go to the Copernicus Science Centre. I will plan everything and send you the details. Let me know what time your train arrives.",
    "Opisz swój udział w szkolnym przedstawieniu": "Last month, I took part in a school play. I played the main character and wore a beautiful costume. At first, I was very nervous, but when I saw my friends in the audience, I felt more confident. The show went great and everyone clapped at the end. It was one of the best days at school.",
    "Podziel się wrażeniami z wydarzenia szkolnego": "Last week, we had a school talent show. Many students performed songs, dances and comedy acts. I was amazed by how talented my classmates are! I really liked the group who played the guitar. The whole event was fun and inspiring. I can’t wait for the next show!"
}

# Ocena poprawności

def ocena_poprawności(tekst):
    try:
        matches = tool.check(tekst)
    except Exception:
        return 0, None, tekst

    bledy = []
    tekst_zaznaczony = tekst

    for match in matches:
        start = match.offset
        end = start + match.errorLength
        blad = tekst[start:end].strip()
        poprawka = match.replacements[0] if match.replacements else "Brak propozycji"
        if not blad:
            continue
        tekst_zaznaczony = tekst_zaznaczony.replace(blad, f"**:red[{blad}]**", 1)
        bledy.append((blad, poprawka, "Błąd gramatyczny"))

    tabela_bledow = pd.DataFrame(bledy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]) if bledy else None
    return 2 if len(bledy) == 0 else 1 if len(bledy) < 5 else 0, tabela_bledow, tekst_zaznaczony

# Ocena treści

def ocena_tresci(tekst, temat):
    if temat not in TEMATY:
        return 0, "Nie wybrano tematu lub temat nieobsługiwany."
    slowa_kluczowe = TEMATY[temat]
    liczba = sum(1 for slowo in slowa_kluczowe if slowo.lower() in tekst.lower())
    if liczba >= 5:
        return 4, "Treść w pełni zgodna z tematem. Świetnie!"
    elif liczba >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif liczba >= 2:
        return 2, "Częściowa zgodność."
    return 1 if liczba == 1 else 0, "Treść nie jest zgodna z tematem."

# Ocena spójności

def ocena_spojnosci(tekst):
    if any(s in tekst.lower() for s in ["however", "therefore", "firstly", "in conclusion"]):
        return 2, "Tekst jest dobrze zorganizowany."
    return 1, "Brakuje spójności logicznej."

# Ocena zakresu

def ocena_zakresu(tekst):
    unikalne = set(tekst.lower().split())
    if len(unikalne) > 40:
        return 2, "Bogate słownictwo!"
    return 1 if len(unikalne) > 20 else 0, "Słownictwo bardzo ubogie."

# Ocena długości

def ocena_dlugosci(tekst):
    liczba = len(tekst.split())
    if liczba >= 50 and liczba <= 120:
        return 2, f"Liczba słów: {liczba} - Poprawna długość."
    return 1, f"Liczba słów: {liczba} - poza zakresem."

# Ocena całkowita

def ocena_tekstu(tekst, temat):
    p1, o1 = ocena_tresci(tekst, temat)
    p2, o2 = ocena_spojnosci(tekst)
    p3, o3 = ocena_zakresu(tekst)
    p4, o4, zaznaczony = ocena_poprawnosci(tekst)
    p5, o5 = ocena_dlugosci(tekst)

    suma = min(p1 + p2 + p3 + p4 + p5, 10)

    wynik = {
        "Treść": f"{p1}/4 - {o1}",
        "Spójność": f"{p2}/2 - {o2}",
        "Zakres": f"{p3}/2 - {o3}",
        "Poprawność": f"{p4}/2 - {o4}",
        "Długość": f"{p5}/2 - {o5}",
        "Łączny wynik": f"{suma}/10 pkt"
    }

    return wynik, o1, o2, o3, o4, o5, zaznaczony, PRZYKLADY.get(temat, "Brak przykładu."), p1 + p2 + p3 + p4 + p5

# Interfejs
st.title("\U0001F4E9 Automatyczna ocena wypowiedzi pisemnej")
selected_temat = st.selectbox("Wybierz temat:", list(TEMATY.keys()))
email_text = st.text_area("Wpisz wypowiedź:")

if st.button("Sprawdź"):
    if email_text:
        wynik, o1, o2, o3, o4, o5, zazn, przyklad, suma = ocena_tekstu(email_text, selected_temat)
        st.subheader("\U0001F4CA Wyniki oceny:")
        for k, v in wynik.items():
            st.write(f"**{k}:** {v}")

        st.subheader("\U0001F4DD Tekst z zaznaczonymi błędami:")
        st.markdown(zazn, unsafe_allow_html=True)

        st.subheader("\U0001F539 Przykład wypowiedzi:")
        st.info(przyklad)
