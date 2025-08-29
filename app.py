# app.py
import streamlit as st
import pandas as pd
from datetime import date
import re
import random
from collections import Counter
import matplotlib.pyplot as plt
import os
import requests

# ==========================
# KONFIGURACJA STRONY
# ==========================
st.set_page_config("Ocena wypowiedzi pisemnej", layout="centered")

# ==========================
# KONFIGURACJA LANGUAGE TOOL (lib + fallback HTTP)
# ==========================
LT_MODE = "lib"
tool = None
try:
    import language_tool_python
    # Publiczne API LanguageTool (działa na Streamlit Cloud, ale z limitami)
    tool = language_tool_python.LanguageToolPublicAPI('en-GB')
except Exception:
    LT_MODE = "http"

LT_ENDPOINT = os.environ.get("LT_ENDPOINT", "https://api.languagetool.org/v2/check")
LT_LANG = "en-GB"

def lt_check_http(text: str):
    """Zapytanie bezpośrednio do publicznego LanguageTool HTTP API (fallback)."""
    try:
        resp = requests.post(
            LT_ENDPOINT,
            data={"text": text, "language": LT_LANG},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        matches = data.get("matches", [])
        # Znormalizowany format
        out = []
        for m in matches:
            out.append({
                "offset": m.get("offset", 0),
                "errorLength": m.get("length", 0),
                "replacements": [r.get("value") for r in m.get("replacements", [])],
                "ruleIssueType": m.get("rule", {}).get("issueType", "unknown")
            })
        return out
    except Exception:
        return []

# ==========================
# TEMATY I SŁOWA KLUCZOWE
# ==========================
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

# Nadużywane słowa (analiza stylu)
OVERUSED = {
    "nice": ["pleasant", "enjoyable", "lovely"],
    "good": ["great", "excellent", "strong"],
    "very": ["really", "extremely", "highly"],
    "a lot": ["many", "plenty of", "a great deal"],
    "big": ["large", "huge", "significant"],
}
CONNECTORS = ["first", "then", "because", "however", "therefore", "in conclusion", "finally", "moreover", "for example"]

# ==========================
# FUNKCJE OCENY
# ==========================
def analiza_poprawnosci(tekst: str):
    """Zwraca: pkt(0-2), tabela błędów, tekst z podkreśleniami, kategorie błędów (Counter)."""
    # Zbieramy wyniki z biblioteki lub z fallbacku HTTP
    matches_std = []
    if LT_MODE == "lib" and tool:
        try:
            matches = tool.check(tekst)
            for m in matches:
                matches_std.append({
                    "offset": m.offset,
                    "errorLength": m.errorLength,
                    "replacements": m.replacements,
                    "ruleIssueType": m.ruleIssueType
                })
        except Exception:
            # awaryjnie przełączamy na HTTP
            matches_std = lt_check_http(tekst)
            st.info("ℹ️ Przełączono na tryb HTTP API (ograniczona analiza).")
    else:
        matches_std = lt_check_http(tekst)
        if matches_std == []:
            st.info("ℹ️ Ograniczona analiza poprawności (brak odpowiedzi z API).")

    błędy = []
    tekst_zaznaczony = tekst

    for m in matches_std:
        start = m["offset"]
        end = start + m["errorLength"]
        błąd = tekst[start:end]
        poprawka = m["replacements"][0] if m["replacements"] else "-"
        if not błąd.strip():
            continue
        tekst_zaznaczony = tekst_zaznaczony.replace(błąd, f"**:red[{błąd}]**", 1)
        błędy.append((błąd, poprawka, m["ruleIssueType"]))

    tabela = pd.DataFrame(błędy, columns=["Błąd", "Poprawna forma", "Typ błędu"]) if błędy \
             else pd.DataFrame(columns=["Błąd", "Poprawna forma", "Typ błędu"])
    # Skala poprawności: 2=bez błędów, 1=<5 błędów, 0=5+ błędów
    if len(błędy) == 0:
        pkt = 2
    elif len(błędy) < 5:
        pkt = 1
    else:
        pkt = 0

    kategorie = Counter([row[2] for row in błędy])
    return pkt, tabela, tekst_zaznaczony, kategorie


def ocena_treści(tekst: str, temat: str):
    słowa = TEMATY.get(temat, [])
    trafienia = sum(1 for s in słowa if s.lower() in tekst.lower())
    if trafienia >= 5: return 4, "Treść zgodna z tematem."
    if trafienia >= 3: return 3, "Dobra zgodność, dodaj więcej szczegółów."
    if trafienia >= 2: return 2, "Częściowa zgodność."
    if trafienia == 1: return 1, "Tylko jeden aspekt tematu."
    return 0, "Treść niezgodna z tematem."


def ocena_spójności(tekst: str):
    if any(w in tekst.lower() for w in ["however", "therefore", "first", "then", "in conclusion", "finally", "moreover"]):
        return 2, "Użyto wyrażeń łączących."
    return 1, "Dodaj więcej łączników (e.g. however, therefore, moreover)."


def ocena_zakresu(tekst: str):
    sl = set(tekst.lower().split())
    if len(sl) > 40: return 2, "Bogaty zakres słów."
    if len(sl) > 20: return 1, "Słownictwo przeciętne."
    return 0, "Słownictwo bardzo ubogie."


def ocena_długości(tekst: str):
    n = len(tekst.split())
    if 50 <= n <= 120:
        return 2, f"Liczba słów: {n} - poprawna."
    return 1 if n < 50 else 0, f"Liczba słów: {n} - poza zakresem (wymagane 50–120)."

# ==========================
# ANALIZA STYLU
# ==========================
def analiza_stylu(tekst: str):
    zdania = [z.strip() for z in re.split(r"(?<=[.!?])\s+", tekst) if z.strip()]
    długości = [len(z.split()) for z in zdania] if zdania else []
    sr = (sum(długości) / len(długości)) if długości else 0.0

    if sr == 0:
        poziom = "brak"
    elif sr < 12:
        poziom = "proste"
    elif sr <= 20:
        poziom = "średnie"
    else:
        poziom = "złożone"

    sugestie = []
    tekst_low = tekst.lower()
    for k, syns in OVERUSED.items():
        if k in tekst_low:
            sugestie.append(f"Zamiast **{k}** spróbuj: *{', '.join(syns)}*.")
    if not any(c in tekst_low for c in [c.lower() for c in CONNECTORS]):
        sugestie.append("Dodaj łączniki: *however, therefore, moreover, for example*.")

    return {
        "liczba_zdań": len(zdania),
        "sr_dł_zdania": round(sr, 1),
        "typ_zdań": poziom,
        "sugestie": sugestie
    }

# ==========================
# ODZNAKI (grywalizacja)
# ==========================
def odznaki(pkt_treść, pkt_spójność, pkt_zakres, pkt_poprawność, pkt_długość):
    badges = []
    if pkt_poprawność == 2:
        badges.append("🏅 Bez błędów!")
    if pkt_zakres == 2:
        badges.append("🌈 Mistrz słownictwa")
    if pkt_spójność == 2:
        badges.append("🧩 Logiczny układ")
    if pkt_treść == 4:
        badges.append("📝 Treść na temat")
    if pkt_długość == 2:
        badges.append("📏 Idealna długość")
    return badges

# ==========================
# MINI-QUIZ (szybka powtórka)
# ==========================
def generuj_quiz():
    pytania = [
        {
            "q": "Który łącznik najlepiej połączy zdania: 'I wanted to go for a walk. It started raining.'",
            "options": ["because", "however", "for example"],
            "answer": "however",
            "explain": "Kontrast: chciałem iść na spacer, jednak zaczęło padać."
        },
        {
            "q": "Wybierz precyzyjniejsze słowo zamiast 'good':",
            "options": ["excellent", "nice", "okay"],
            "answer": "excellent",
            "explain": "'Excellent' jest bardziej precyzyjne i silniejsze niż 'good'."
        },
        {
            "q": "Wybierz poprawną formę zdania w Past Simple:",
            "options": ["Yesterday I go to school.", "Yesterday I went to school.", "Yesterday I going to school."],
            "answer": "Yesterday I went to school.",
            "explain": "Past Simple: went."
        }
    ]
    random.shuffle(pytania)
    return pytania[:3]

# ==========================
# STAN APLIKACJI – HISTORIA
# ==========================
if "historia" not in st.session_state:
    st.session_state["historia"] = []  # {data, temat, punkty}

# ==========================
# UI
# ==========================
st.title("📩 Automatyczna ocena wypowiedzi pisemnej")
st.write(f"**Data:** {date.today().isoformat()}")
st.info("Cześć! Napisz tekst na wybrany temat, a ja pokażę Ci wynik, podpowiedzi i mini-quiz. 🚀")

temat = st.selectbox("🎯 Wybierz temat:", list(TEMATY.keys()))
tekst = st.text_area("✍️ Wpisz tutaj swój tekst (50–120 słów):", height=200)

if st.button("✅ Sprawdź"):
    # Ocena
    pkt_treść, op_treść = ocena_treści(tekst, temat)
    pkt_spójność, op_spójność = ocena_spójności(tekst)
    pkt_zakres, op_zakres = ocena_zakresu(tekst)
    pkt_długość, op_długość = ocena_długości(tekst)
    pkt_poprawność, tabela, zaznaczony, kategorie = analiza_poprawnosci(tekst)

    suma = min(pkt_treść + pkt_spójność + pkt_zakres + pkt_poprawność + pkt_długość, 10)

    # 🎮 Pasek postępu + metryka
    st.subheader("🎮 Twój wynik i postęp")
    st.progress(suma / 10)
    st.metric(label="Łączny wynik", value=f"{suma}/10")

    # 📊 Wyniki szczegółowe
    st.markdown("## 📊 Wyniki oceny")
    st.write(f"**Treść:** {pkt_treść}/4 – {op_treść}")
    st.write(f"**Spójność:** {pkt_spójność}/2 – {op_spójność}")
    st.write(f"**Zakres:** {pkt_zakres}/2 – {op_zakres}")
    st.write(f"**Poprawność:** {pkt_poprawność}/2 – Im mniej błędów, tym lepiej!")
    st.write(f"**Długość:** {pkt_długość}/2 – {op_długość}")

    # 🏆 Odznaki
    badges = odznaki(pkt_treść, pkt_spójność, pkt_zakres, pkt_poprawność, pkt_długość)
    if badges:
        st.markdown("### 🏆 Zdobyte odznaki")
        st.success("  •  ".join(badges))

    # 🧠 Analiza stylu
    st.markdown("## 🧠 Analiza stylu")
    styl = analiza_stylu(tekst)
    st.write(f"Liczba zdań: **{styl['liczba_zdań']}** | Średnia długość zdania: **{styl['sr_dł_zdania']}** słów | Typ zdań: **{styl['typ_zdań']}**")
    if styl['sugestie']:
        st.info("\n".join([f"• {s}" for s in styl['sugestie']]))
    else:
        st.success("Styl wygląda dobrze! Kontynuuj w tym kierunku.")

    # ❌ Lista błędów
    if not tabela.empty:
        st.markdown("## ❌ Lista błędów i poprawki")
        st.dataframe(tabela, use_container_width=True)

    # 📝 Tekst z błędami
    st.markdown("## 📝 Tekst z zaznaczonymi błędami")
    st.markdown(zaznaczony, unsafe_allow_html=True)

    # 🧩 Mini-quiz
    st.markdown("## 🧩 Szybka powtórka (mini-quiz)")
    pytania = generuj_quiz()
    if 'quiz_odp' not in st.session_state:
        st.session_state.quiz_odp = {}
    poprawne = 0
    for i, p in enumerate(pytania):
        odp = st.radio(f"{i+1}. {p['q']}", p['options'], key=f"quiz_{i}")
        st.session_state.quiz_odp[i] = (odp, p['answer'], p['explain'])
    if st.button("📥 Sprawdź odpowiedzi"):
        for i, (u, ans, expl) in st.session_state.quiz_odp.items():
            if u == ans:
                poprawne += 1
                st.success(f"{i+1}. ✅ Dobrze! ({ans})")
            else:
                st.error(f"{i+1}. ❌ Poprawna: {ans}. {expl}")
        st.info(f"Wynik quizu: **{poprawne}/{len(st.session_state.quiz_odp)}**")

    # 💾 Zapis do historii
    st.session_state["historia"].append({
        "data": date.today().isoformat(),
        "temat": temat,
        "punkty": suma
    })

# --- 📈 Sekcja progresu ---
if st.session_state["historia"]:
    st.markdown("---")
    st.subheader("📚 Historia Twoich wyników")
    hist_df = pd.DataFrame(st.session_state["historia"])
    st.dataframe(hist_df, use_container_width=True)

    st.subheader("📈 Twój progres")
    hist_plot = hist_df.tail(10).reset_index(drop=True)
    fig, ax = plt.subplots()
    ax.plot(hist_plot.index + 1, hist_plot["punkty"], marker="o")
    ax.set_xlabel("Próba")
    ax.set_ylabel("Punkty")
    ax.set_ylim(0, 10)
    ax.set_title("Postępy w ocenach (ostatnie 10 prób)")
    st.pyplot(fig)
