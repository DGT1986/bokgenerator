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
    
    # Generer boktekst
    boktekst = f"Generert boktekst for {kategori} på {språk}."  # Her skal genereringen av boken skje
    txt_fil = f"{kategori}.txt"
    with open(txt_fil, "w", encoding="utf-8") as f:
        f.write(boktekst)

    st.subheader("📖 Din Genererte Bok:")
    st.text_area("Boktekst", boktekst, height=500)
    st.download_button("📥 Last ned som TXT", open(txt_fil, "rb"), file_name=txt_fil)

    if ekspertmodus:
        st.subheader("💰 Anbefalt bokpris:")
        prisstrategi = foreslå_bokpris(kategori, valgt_språk)
        st.text_area("Prisstrategi", prisstrategi, height=100)

    if analysemodus:
        st.subheader("📊 Analyse av bokens salgspotensial:")
        analyse_resultat = analyser_og_rate_bok(boktekst, kategori, valgt_språk)
        st.text_area("Analyse og forbedringer", analyse_resultat, height=200)
