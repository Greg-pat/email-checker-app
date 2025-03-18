import streamlit as st
import language_tool_python
import pandas as pd

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki (British English)
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# ✅ Pełna lista tematów egzaminacyjnych
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

# ✅ Funkcja oceniająca poprawność językową i podkreślająca błędy
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

        tekst_zaznaczony = tekst_zaznaczony.replace(
            błąd, f"**:red[{błąd}]**", 1
        )

        błędy.append((błąd, poprawka, "Błąd gramatyczny"))

    tabela_błędów = pd.DataFrame(
        błędy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]
    ) if błędy else None

    return 2 if len(błędy) == 0 else 1 if len(błędy) < 5 else 0, tabela_błędów, tekst_zaznaczony

# ✅ Funkcja oceniająca treść (0-4 pkt)
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

# ✅ Funkcja oceniająca spójność i logikę (0-2 pkt)
def ocena_spójności(tekst):
    if any(s in tekst.lower() for s in ["however", "therefore", "firstly", "in conclusion"]):
        return 2, "Tekst jest dobrze zorganizowany."
    return 1, "Spójność może być lepsza – użyj więcej wyrażeń łączących."

# ✅ Funkcja oceniająca zakres środków językowych (0-2 pkt)
def ocena_zakresu(tekst):
    unikalne_słowa = set(tekst.lower().split())
    if len(unikalne_słowa) > 40:
        return 2, "Bardzo bogate słownictwo!"
    return 1 if len(unikalne_słowa) > 20 else 0, "Słownictwo jest zbyt proste."

# ✅ Główna funkcja oceny (maksymalnie 10 pkt)
def ocena_tekstu(tekst, temat):
    punkty_treści, opis_treści = ocena_treści(tekst, temat)
    punkty_spójności, opis_spójności = ocena_spójności(tekst)
    punkty_zakresu, opis_zakresu = ocena_zakresu(tekst)
    punkty_poprawności, tabela_błędów, tekst_zaznaczony = ocena_poprawności(tekst)

    suma_punktów = min(punkty_treści + punkty_spójności + punkty_zakresu + punkty_poprawności, 10)  

    rekomendacje = []
    if punkty_treści < 4:
        rekomendacje.append("📌 **Treść**: Dodaj więcej szczegółów i rozwiń swoje pomysły.")
    if punkty_spójności < 2:
        rekomendacje.append("📌 **Spójność**: Użyj więcej wyrażeń łączących, np. *however, therefore, in addition*.")
    if punkty_zakresu < 2:
        rekomendacje.append("📌 **Zakres słownictwa**: Użyj bardziej różnorodnych słów.")
    if punkty_poprawności < 2:
        rekomendacje.append("📌 **Poprawność**: Sprawdź błędy gramatyczne i ortograficzne.")

    wyniki = {
        '📝 Treść': f"{punkty_treści}/4 - {opis_treści}",
        '🔗 Spójność i logika': f"{punkty_spójności}/2 - {opis_spójności}",
        '📖 Zakres językowy': f"{punkty_zakresu}/2 - {opis_zakresu}",
        '✅ Poprawność językowa': f"{punkty_poprawności}/2 - Im mniej błędów, tym lepiej!",
        '📌 **Łączny wynik:**': f"🔹 **{suma_punktów}/10 pkt**",
        '💡 **Jak poprawić pracę?**': rekomendacje
    }
    
    return wyniki, tabela_błędów, tekst_zaznaczony

# ✅ **Interfejs użytkownika**
st.set_page_config(page_title="Ocena pisemnych wypowiedzi", layout="centered")

st.title("📩 Automatyczna ocena pisemnych wypowiedzi")
selected_temat = st.selectbox("📌 Wybierz temat:", list(TEMATY.keys()))
email_text = st.text_area("✏️ Wpisz swój tekst tutaj:")

if st.button("✅ Sprawdź"):
    if email_text:
        wynik, tabela_błędów, tekst_zaznaczony = ocena_tekstu(email_text, selected_temat)

        st.subheader("📊 Wyniki oceny:")
        for klucz, wartość in wynik.items():
            st.write(f"**{klucz}:** {wartość}")
