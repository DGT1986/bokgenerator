import openai
import os
import streamlit as st
import requests
from ebooklib import epub
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Last inn API-nøkkel fra .env-fil
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Opprett OpenAI-klient
client = openai.Client(api_key=api_key)

# 🔹 Bestselgende Amazon KDP-kategorier
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

# 🔹 Språkvalg optimalisert for Amazon KDP
språkvalg = {
    "Engelsk": "en",
    "Spansk": "es",
    "Tysk": "de",
    "Fransk": "fr",
    "Italiensk": "it",
    "Norsk": "no",
    "Nederlandsk": "nl",
    "Portugisisk": "pt"
}

# 🔹 Funksjoner for optimalisering

def analyser_og_rate_bok(boktekst, nisje, språk):
    prompt = f"""
    Evaluer denne teksten opp mot bestselgende bøker innen {nisje} på Amazon KDP. 
    Gi en score fra 1-100 basert på:
    - Lesbarhet
    - Engasjement
    - SEO-optimalisering
    - Kommersiell appell
    Gi også forbedringsforslag for å øke salget. Skriv svaret på {språk}.
    
    Tekst:
    {boktekst}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def foreslå_bokpris(nisje, språk):
    prompt = f"""
    Analyser prisene på de bestselgende bøkene innen {nisje} på Amazon KDP og foreslå en optimal prisstrategi 
    for å maksimere volum-salg. Vurder:
    - Anbefalt prisnivå for Kindle e-bok, paperback og hardcover.
    - Psykologiske prispunkter som gir høyere konvertering ($2.99, $4.99, $9.99 osv.).
    - Hvordan Kindle Unlimited kan påvirke salget.
    - Kampanjestrategier for å booste volum.
    - Hva de mest suksessrike forfatterne innen {nisje} gjør med prissetting.
    
    Skriv svaret på {språk}.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# 🔹 Streamlit-app
st.title("📖 AI Bestselger-Bokgenerator for Amazon KDP")

ekspertmodus = st.checkbox("Ekspertmodus: Aktiver alle optimaliseringsverktøy")
analysemodus = st.checkbox("Analysemodus: Evaluer bokens salgspotensial")

språk = st.selectbox("Velg språk for boken:", list(språkvalg.keys()))
kategori = st.selectbox("Velg en bestselgende kategori:", ["Velg en kategori..."] + bestseller_nisjer)
antall_kapitler = st.slider("Velg antall kapitler", min_value=3, max_value=10, value=5)

if st.button("Generer Bok"):
    st.info("Genererer boken, vennligst vent...")
    valgt_språk = språkvalg[språk]
    
    def generer_bok(nisje, antall_kapitler, språk):
    kapittel_prompt = f"Generer en kapitteloversikt for en bestselgende bok om {nisje} med {antall_kapitler} kapitler. Skriv på {språk}."
    
    kapittel_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": kapittel_prompt}],
        temperature=0.7
    )
    
    kapitler = kapittel_response.choices[0].message.content.split("\n")

    bok_tekst = f"# {nisje} - AI-generert bok ({språk})\n\n"
    
    for i, kapittel in enumerate(kapitler[:antall_kapitler]):
        if kapittel.strip():
            kapittel_prompt = f"""
            Skriv et detaljert kapittel med tittelen '{kapittel}' for en bestselgende bok om {nisje}. 
            Inkluder actionable tips, eksempler og praktiske øvelser. 
            Skriv i en engasjerende og lettlest stil. Skriv på {språk}.
            """
            
            kapittel_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": kapittel_prompt}],
                temperature=0.7
            )
            
            kapittel_tekst = kapittel_response.choices[0].message.content
            bok_tekst += f"## Kapittel {i+1}: {kapittel}\n\n{kapittel_tekst}\n\n"

    return bok_tekst
