import openai
import os
import streamlit as st
from dotenv import load_dotenv

# Last inn API-nøkkel fra .env-fil
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Opprett OpenAI-klient
client = openai.Client(api_key=api_key)

# Populære emner som selger godt på Amazon KDP
bestseller_nisjer = [
    "Selvhjelp og personlig utvikling",
    "Penger og investeringer",
    "Online business og passiv inntekt",
    "Produktivitet og vaner",
    "Mental helse og mindfulness",
    "AI og teknologi",
    "Vekttap og helse",
    "Dating og relasjoner",
    "Spirituell vekst",
    "Reiseskildringer og nomadeliv"
]

# Funksjon for å finne trender og optimalisere bokens innhold
def finn_populært_emne(nisje):
    prompt = f"Hvilke spesifikke emner innen {nisje} selger best på Amazon Kindle? Gi en liste over 5 populære boktitler og hva de har til felles."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du er en ekspert på Amazon KDP og bokmarkedet."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Funksjon for å generere en optimalisert bok basert på trender
def generer_optimalisert_bok(nisje, antall_kapitler):
    emne_trender = finn_populært_emne(nisje)

    kapittel_prompt = f"Basert på populære bøker innen {nisje}, lag en kapitteloversikt for en kort bok på {antall_kapitler} kapitler."
    
    kapittel_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du er en bestselgende forfatter."},
            {"role": "user", "content": kapittel_prompt}
        ],
        temperature=0.7
    )
    
    kapittel_oversikt = kapittel_response.choices[0].message.content
    kapitler = kapittel_oversikt.split("\n")  # Deler opp kapitler

    # Generer fullstendig tekst for hvert kapittel
    bok_tekst = f"# {nisje} - Bestselger\n\n{emne_trender}\n\n"
    for i, kapittel in enumerate(kapitler[:antall_kapitler]):
        if kapittel.strip():
            kapittel_prompt = f"Skriv et detaljert kapittel med tittelen '{kapittel}' for en bestselgende bok innen {nisje}. Inkluder actionable tips, statistikk og gode historier."
            
            kapittel_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Du skriver på en lettlest og engasjerende måte."},
                    {"role": "user", "content": kapittel_prompt}
                ],
                temperature=0.7
            )
            
            kapittel_tekst = kapittel_response.choices[0].message.content
            bok_tekst += f"## Kapittel {i+1}: {kapittel}\n\n{kapittel_tekst}\n\n"

    return bok_tekst

# Streamlit-app for å lage en bestselger-bok
st.title("📖 AI Bestselger-Bokgenerator")

nisje = st.selectbox("Velg en bestselger-nisje:", bestseller_nisjer)
antall_kapitler = st.slider("Velg antall kapitler", min_value=3, max_value=10, value=5)

if st.button("Generer Bestselger-Bok"):
    if nisje:
        st.info("Genererer en optimalisert bok, vennligst vent...")
        bok = generer_optimalisert_bok(nisje, antall_kapitler)
        st.subheader("Din bestselgende bok:")
        st.text_area("Boktekst", bok, height=500)
    else:
        st.warning("Velg en nisje først.")
