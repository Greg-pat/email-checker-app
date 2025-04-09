import streamlit as st
import language_tool_python
import pandas as pd

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki (British English)
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# ✅ Lista tematów egzaminacyjnych + przykładowe wypowiedzi
TEMATY = {
    "Opisz swoje ostatnie wakacje": {
        "słowa": ["holiday", "trip", "beach", "mountains", "memories", "visited", "hotel"],
        "przyklad": "Last summer, I went to the mountains with my family. We hiked every day and stayed in a small wooden cabin. The weather was perfect, and we enjoyed delicious local food. My favourite part was swimming in a crystal-clear lake. I took many photos and made wonderful memories. It was the best holiday I've ever had."
    },
    "Napisz o swoich planach na najbliższy weekend": {
        "słowa": ["weekend", "going to", "plan", "cinema", "friends", "family"],
        "przyklad": "This weekend, I'm going to visit my grandparents in the countryside. On Saturday, we are planning a small barbecue with the whole family. I will help my grandfather in the garden and play board games with my cousins. On Sunday, we will go for a long walk in the forest. I always enjoy spending time there."
    },
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": {
        "słowa": ["meet", "visit", "place", "Poland", "invite", "schedule"],
        "przyklad": "Hi Alex! I heard you are visiting Poland next month. I'd love to meet and show you some great places in my city. We could go sightseeing, try some traditional Polish food, and maybe attend a concert. Let me know what dates work for you so we can plan everything. Can't wait to see you!"
    }
}

# ✅ Funkcja do oceny poprawności

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

        tekst_zaznaczony = tekst_zaznaczony.replace(
            blad, f"**:red[{blad}]**", 1
        )

        bledy.append((blad, poprawka, "Błąd gramatyczny"))

    tabela_bledow = pd.DataFrame(
        bledy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if bledy else None

    return 2 if len(bledy) == 0 else 1 if len(bledy) < 5 else 0, tabela_bledow, tekst_zaznaczony

# ✅ Funkcje oceny kryteriów

def ocena_tresci(tekst, temat):
    if temat not in TEMATY:
        return 0, "Nie wybrano tematu lub temat nieobsługiwany."

    slowa_kluczowe = TEMATY[temat]["słowa"]
    liczba = sum(1 for s in slowa_kluczowe if s.lower() in tekst.lower())

    if liczba >= 5:
        return 4, "Treść w pełni zgodna z tematem. Świetnie!"
    elif liczba >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif liczba >= 2:
        return 2, "Częściowa zgodność."
    return 1 if liczba == 1 else 0, "Treść nie jest zgodna z tematem."

def ocena_spojnosci(tekst):
    if any(s in tekst.lower() for s in ["however", "therefore", "firstly", "in conclusion"]):
        return 2, "Tekst jest dobrze zorganizowany."
    return 1, "Brakuje spójności logicznej."

def ocena_zakresu(tekst):
    slowa = set(tekst.lower().split())
    if len(slowa) > 40:
        return 2, "Bardzo bogate słownictwo!"
    return 1 if len(slowa) > 20 else 0, "Słownictwo bardzo ubogie."

def ocena_dlugosci(tekst):
    liczba = len(tekst.split())
    if 50 <= liczba <= 120:
        return 2, f"Liczba słów: {liczba} - Poprawna długość."
    return 1 if 30 <= liczba < 50 or liczba > 120 else 0, f"Liczba słów: {liczba} - poza zakresem."

# ✅ Główna funkcja

def ocena_tekstu(email_text, temat):
    p1, o1 = ocena_tresci(email_text, temat)
    p2, o2 = ocena_spojnosci(email_text)
    p3, o3 = ocena_zakresu(email_text)
    p4, o4, zaznaczony = ocena_poprawnosci(email_text)
    p5, o5 = ocena_dlugosci(email_text)

    suma = min(p1 + p2 + p3 + p4 + p5, 10)
    przyklad = TEMATY[temat]["przyklad"]
    wynik = {
        "Treść": f"{p1}/4 - {o1}",
        "Spójność": f"{p2}/2 - {o2}",
        "Zakres": f"{p3}/2 - {o3}",
        "Poprawność": f"{p4}/2 - {o4}",
        "Długość": f"{p5}/2 - {o5}",
        "Ὄc Łączny wynik:": f"{suma}/10 pkt"
    }
    return wynik, o1, o2, o3, o4, o5, zaznaczony, przyklad, suma
