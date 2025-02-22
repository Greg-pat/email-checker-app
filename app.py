import streamlit as st
import language_tool_python
from spellchecker import SpellChecker
import pandas as pd
import re

# ✅ Pobieramy narzędzie LanguageTool do sprawdzania gramatyki (British English)
tool = language_tool_python.LanguageToolPublicAPI('en-GB')
spell = SpellChecker(language='en')

# ✅ Tematy i wymagane słowa kluczowe
TEMATY = {
    "Blog o nowinkach technicznych": ["technology", "innovation", "AI", "robot", "device", "software", "gadget"],
    "E-mail o spotkaniu klasowym": ["meeting", "class", "school", "date", "time", "place", "invitation"]
}

# ✅ Funkcja oceniająca treść pod kątem zgodności z tematem
def ocena_merytoryczna(tekst, temat):
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
    elif liczba_wystąpień == 1:
        return 1, "Treść ledwo nawiązuje do tematu. Spróbuj dodać więcej informacji."
    return 0, "Treść nie jest zgodna z tematem. Przemyśl jeszcze raz polecenie."

# ✅ Funkcja oceniająca poprawność językową i podkreślająca błędy
def ocena_poprawności(tekst):
    matches = tool.check(tekst)
    błędy = []
    tekst_zaznaczony = tekst

    for match in matches:
        błąd = match.context[match.offset:match.offset + match.errorLength]
        poprawka = match.replacements[0] if match.replacements else "Brak propozycji"
        błędy.append((błąd, poprawka, "Błąd gramatyczny"))
        tekst_zaznaczony = re.sub(rf'\b{re.escape(błąd)}\b', f"<span style='color:red; font-weight:bold;'>{błąd}</span>", tekst_zaznaczony, 1)

    tabela_błędów = pd.DataFrame(błędy, columns=["🔴 Błąd", "✅ Poprawna forma", "ℹ️ Typ błędu"]) if błędy else None

    return 2 if len(błędy) == 0 else 1 if len(błędy) < 5 else 0, tabela_błędów, tekst_zaznaczony

# ✅ Główna funkcja oceny
def ocena_tekstu(tekst, temat):
    punkty_treści, opis_treści = ocena_merytoryczna(tekst, temat)
    punkty_poprawności, tabela_błędów, tekst_zaznaczony = ocena_poprawności(tekst)

    wyniki = {
        '📖 Ocena treści (zgodność z tematem)': f"{punkty_treści}/4 - {opis_treści}",
        '✅ Poprawność językowa': f"{punkty_poprawności}/2 - Im mniej błędów, tym lepiej!",
        '📌 **Łączny wynik:**': f"🔹 **{punkty_treści + punkty_poprawności}/6 pkt**"
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

        if tabela_błędów is not None and not tabela_błędów.empty:
            st.write("### ❌ Lista błędów i poprawek:")
            st.dataframe(tabela_błędów, height=300, width=700)

        st.write("### 🔍 Tekst z zaznaczonymi błędami:")
        st.markdown(f"<p style='font-size:16px;'>{tekst_zaznaczony}</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Wpisz tekst przed sprawdzeniem.")
