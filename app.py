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

# Przykładowe idealne odpowiedzi
PRZYKLADY = {
    "Opisz swoje ostatnie wakacje": "Last summer, I went on holiday to the seaside with my family. We stayed in a small hotel near the beach. Every day we swam, played volleyball and ate ice cream. My best memory is a boat trip we took at sunset. The view was beautiful and I took many photos. It was an amazing holiday and I want to go there again. I also made a new friend from another city. We still talk online sometimes.",
    "Napisz o swoich planach na najbliższy weekend": "This weekend, I am going to visit my grandparents. On Saturday, we are going to cook dinner together and play board games. On Sunday, I plan to go to the cinema with my cousin. We want to watch a new comedy film. I’m really looking forward to this weekend! If the weather is good, we’ll also go for a walk in the park. I hope everything goes as planned.",
    "Zaproponuj spotkanie koledze/koleżance z zagranicy": "Hi Alex! I’m so happy you are coming to Poland! Would you like to meet on Saturday afternoon? We can go to the Old Town and have lunch in a nice café. Then I can show you the castle and we can take some photos. Let me know if that works for you! If not, we can also meet on Sunday. I can’t wait to see you!",
    "Opisz swój udział w szkolnym przedstawieniu": "Last month, I took part in a school play. I played the role of a prince. At first, I was very nervous, but later I felt confident. We practised a lot before the performance. My parents and friends came to watch me. It was a great experience and I really enjoyed it. After the show, we took a group photo. I will always remember that day.",
    "Podziel się wrażeniami z wydarzenia szkolnego": "Last week, our school organised a music competition. I sang a song with my best friend. We practised every day for a week. There were many talented students. We didn’t win, but we had fun. I will never forget this event because it helped me feel more confident. Our teacher said we did a good job. I hope we can take part again next year.",
    "Opisz swoje nowe hobby": "Two months ago, I started learning how to play the guitar. I practise every day after school. I chose this hobby because I love music. Now I can play simple songs. I think playing an instrument is fun and relaxing. I want to play in a school band in the future. My parents say I’m making good progress. I even played a song for my friends last weekend.",
    "Opowiedz o swoich doświadczeniach związanych z nauką zdalną": "During the pandemic, I had online lessons. I liked learning at home because I could wake up later. However, I missed my friends and teachers. Sometimes it was hard to understand new topics without help. I think online learning has both advantages and disadvantages. It also made me more responsible and independent. I prefer going to school now, but I learned a lot from that time.",
    "Opisz szkolną wycieczkę, na której byłeś": "Last autumn, I went on a school trip to Kraków. We visited Wawel Castle, the market square and a museum. I took a lot of photos and bought souvenirs. My favourite part was walking around the old streets with my friends. It was an unforgettable trip! We also had lunch in a traditional Polish restaurant. I hope to go there again with my family.",
    "Zaproponuj wspólne zwiedzanie ciekawych miejsc w Polsce": "Hi Emma! When you visit Poland, let’s go sightseeing together! I want to show you Warsaw – the capital city. We can visit the Old Town, the Royal Castle, and go to the Copernicus Science Centre. I think you’ll really enjoy it! We can also try some Polish food like pierogi and go shopping. Let me know what you think and when you’re free!"
}

# ... (pozostała część kodu bez zmian)

# Po ocenie pracy
        st.markdown("### \U0001F4D6 Przykład idealnej wypowiedzi:")
        st.info(PRZYKLADY.get(selected_temat, "Brak przykładowej odpowiedzi dla tego tematu."))
