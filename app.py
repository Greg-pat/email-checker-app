import streamlit as st
import language_tool_python
import pandas as pd

# Narzędzie do sprawdzania poprawności językowej
tool = language_tool_python.LanguageToolPublicAPI('en-GB')

# Tematy i słowa kluczowe
TEMATY = {
    "Opisz swoje ostatnie wakacje": [
        "holiday", "trip", "beach", "mountains", "memories", "visited", "hotel"
    ],
    "Napisz o swoich planach na najbliższy weekend": [
        "weekend", "going to", "plan", "cinema", "friends", "family"
    ],
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": [
        "meet", "visit", "place", "Poland", "invite", "schedule"
    ],
    "Opisz swój udział w szkolnym przedstawieniu": [
        "school play", "role", "stage", "acting", "performance", "nervous"
    ],
    "Podziel się wrażeniami z wydarzenia szkolnego": [
        "event", "competition", "school", "experience", "memorable"
    ],
    "Opisz swoje nowe hobby": [
        "hobby", "started", "enjoy", "benefits", "passion"
    ],
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną": [
        "online learning", "advantages", "disadvantages", "difficult"
    ],
    "Opisz szkolną wycieczkę, na której byłeś": [
        "school trip", "visited", "museum", "amazing", "historical"
    ],
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": [
        "sightseeing", "places", "Poland", "tour", "recommend"
    ],
}

PRZYKLADY = {
    "Opisz swoje ostatnie wakacje": "Last summer, I went to the mountains with my family. We hiked every day and stayed in a small wooden cabin. One day, we reached the top of a mountain and admired the beautiful views. We also made campfires in the evenings and told stories. It was the most relaxing trip I've ever had. I will remember it forever.",
    "Napisz o swoich planach na najbliższy weekend": "This weekend, I am going to visit my grandparents. On Saturday, we will bake a cake and go for a walk in the park. In the evening, I plan to watch a film with my family. On Sunday, I will do my homework and read a book. I hope the weather will be nice. I can't wait!",
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": "Hi Alex! When you come to Poland next month, we could meet in Warsaw. I can show you the Old Town and we can try traditional Polish food. There's also a cool science centre and a nice park nearby. We could go for a bike ride if you like. Let me know what you think!",
    "Opisz swój udział w szkolnym przedstawieniu": "Last month, I took part in a school play. I played the main role, and I was very nervous before going on stage. Luckily, everything went well and the audience loved it. We rehearsed for weeks to make the performance perfect. My classmates were amazing. It was an unforgettable experience!",
    "Podziel się wrażeniami z wydarzenia szkolnego": "Last Friday, we had a school talent show. Many students performed songs, dances, and magic tricks. I was impressed by how talented everyone was. My best friend sang a beautiful song and won first place. The atmosphere was friendly and fun. It was one of the best days at school!",
    "Opisz swoje nowe hobby": "Recently, I started learning how to draw. I practise almost every day and I enjoy sketching nature and animals. It's a relaxing activity that helps me concentrate. I've already filled one sketchbook with my drawings. My family says I’m improving fast. I’m really proud of my progress.",
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną": "During the pandemic, I had to study from home. At first, it was difficult to focus and understand the lessons. Over time, I got used to it and learned to manage my time better. I missed my friends and the school atmosphere. But I also enjoyed working at my own pace. It was a unique experience.",
    "Opisz szkolną wycieczkę, na której byłeś": "Last autumn, we went on a school trip to Kraków. We visited Wawel Castle and the Main Market Square. Our guide told us many interesting stories about the city’s history. We also went to a museum and had lunch in a nice restaurant. I took a lot of photos. It was an educational and fun day!",
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": "Dear Emma, if you come to Poland, I suggest visiting Kraków. It's full of history and beautiful architecture. We could go to the salt mine in Wieliczka and walk around the old town. I’d also take you to Zakopane in the mountains. Let me know when you are free!",
}

# Funkcje oceny

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
    tabela = pd.DataFrame(błędy, columns=["Błąd", "Poprawna forma", "Typ błędu"]) if błędy else None
    return 2 if len(błędy) == 0 else 1 if len(błędy) < 5 else 0, tabela, tekst_zaznaczony

def ocena_treści(tekst, temat):
    słowa_kluczowe = TEMATY.get(temat, [])
    liczba = sum(1 for słowo in słowa_kluczowe if słowo.lower() in tekst.lower())
    if liczba >= 5:
        return 4, "Treść zgodna z tematem. Świetnie!"
    elif liczba >= 3:
        return 3, "Dobra zgodność, ale można dodać więcej szczegółów."
    elif liczba >= 2:
        return 2, "Częściowa zgodność."
    elif liczba >= 1:
        return 1, "Temat częściowo ujęty, ale bardzo ogólnie."
    else:
        return 0, "Treść niezgodna z tematem."

def ocena_spójności(tekst):
    if any(w in tekst.lower() for w in ["however", "therefore", "firstly", "finally", "in conclusion"]):
        return 2, "Tekst dobrze zorganizowany."
    return 1, "Brakuje spójności logicznej."

def ocena_zakresu(tekst):
    unikalne = set(tekst.lower().split())
    if len(unikalne) > 40:
        return 2, "Słownictwo bardzo bogate."
    elif len(unikalne) > 20:
        return 1, "Słownictwo umiarkowanie zróżnicowane."
    return 0, "Słownictwo bardzo ubogie."

def ocena_długości(tekst):
    liczba = len(tekst.split())
    if 50 <= liczba <= 120:
        return 2, f"Liczba słów: {liczba} - Poprawna."
    return 1, f"Liczba słów: {liczba} - poza zakresem."

def ocena_tekstu(tekst, temat):
    o1, t1 = ocena_treści(tekst, temat)
    o2, t2 = ocena_spójności(tekst)
    o3, t3 = ocena_zakresu(tekst)
    o4, tabela, zazn = ocena_poprawności(tekst)
    o5, t5 = ocena_długości(tekst)
    suma = min(o1 + o2 + o3 + o4 + o5, 10)
    return {
        "Treść": f"{o1}/4 - {t1}",
        "Spójność": f"{o2}/2 - {t2}",
        "Zakres": f"{o3}/2 - {t3}",
        "Poprawność": f"{o4}/2 - Im mniej błędów, tym lepiej!",
        "Długość": f"{o5}/2 - {t5}",
        "Łączny wynik": f"{suma}/10 pkt"
    }, tabela, zazn, PRZYKLADY.get(temat, "Brak przykładu.")

# UI
st.set_page_config("Ocena wypowiedzi", layout="centered")
st.title("📩 Automatyczna ocena wypowiedzi pisemnej")
st.markdown(f"**Data:** {pd.Timestamp.today().date()}")

selected_temat = st.selectbox("📌 Wybierz temat wypowiedzi:", list(TEMATY.keys()))
email_text = st.text_area("✍️ Wpisz swoją wypowiedź:", height=200)

if st.button("✅ Sprawdź"):
    if email_text:
        wynik, tabela, zazn, przykład = ocena_tekstu(email_text, selected_temat)

        st.subheader("📊 Wyniki oceny:")
        for k, v in wynik.items():
            st.write(f"**{k}:** {v}")

        if tabela is not None:
            st.subheader("❌ Lista błędów i poprawek:")
            st.dataframe(tabela, use_container_width=True)

        st.subheader("📝 Tekst z zaznaczonymi błędami:")
        st.markdown(zazn, unsafe_allow_html=True)

        st.subheader("🟦 Przykład wypowiedzi:")
        st.info(przykład)
