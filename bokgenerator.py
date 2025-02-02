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

# Populære emner for Amazon KDP
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

# Funksjon for å generere SEO-optimalisert metadata
def generer_metadata(tittel, nisje):
    prompt = f"Generer en Amazon KDP-optimalisert beskrivelse og søkeord for boken '{tittel}' innen {nisje}. Bruk språket til bestselgere."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Funksjon for å generere et bokomslag med DALL·E
def generer_omslag(tittel):
    prompt = f"Lag et bokomslag for en bestselgende bok med tittelen '{tittel}'. Omslaget bør være profesjonelt, minimalistisk og ha en moderne stil."
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024"
    )
    
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))
    
    filnavn = f"{tittel}_omslag.jpg"
    image.save(filnavn)
    return filnavn

# Funksjon for å generere bokinnhold
def generer_bok(nisje, antall_kapitler):
    kapittel_prompt = f"Generer en kapitteloversikt for en bestselgende bok om {nisje} med {antall_kapitler} kapitler."
    
    kapittel_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": kapittel_prompt}],
        temperature=0.7
    )
    
    kapitler = kapittel_response.choices[0].message.content.split("\n")

    bok_tekst = f"# {nisje} - AI-generert bok\n\n"
    for i, kapittel in enumerate(kapitler[:antall_kapitler]):
        if kapittel.strip():
            kapittel_prompt = f"Skriv et detaljert kapittel med tittelen '{kapittel}' for en bestselgende bok om {nisje}. Inkluder actionable tips og eksempler."
            kapittel_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": kapittel_prompt}],
                temperature=0.7
            )
            kapittel_tekst = kapittel_response.choices[0].message.content
            bok_tekst += f"## Kapittel {i+1}: {kapittel}\n\n{kapittel_tekst}\n\n"

    return bok_tekst

# Funksjon for å lage en nedlastbar tekstfil
def lag_txt(boktittel, bokinnhold):
    filnavn = f"{boktittel}.txt"
    with open(filnavn, "w", encoding="utf-8") as f:
        f.write(bokinnhold)
    return filnavn

# Streamlit-app
st.title("📖 AI Bestselger-Bokgenerator for Amazon KDP")

nisje = st.selectbox("Velg en bestselger-nisje:", bestseller_nisjer)
antall_kapitler = st.slider("Velg antall kapitler", min_value=3, max_value=10, value=5)

if st.button("Generer Bok"):
    if nisje:
        st.info("Genererer boken, vennligst vent...")
        boktekst = generer_bok(nisje, antall_kapitler)
        txt_fil = lag_txt(nisje, boktekst)
        metadata = generer_metadata(nisje, nisje)
        omslag_fil = generer_omslag(nisje)

        st.subheader("Din genererte bok:")
        st.text_area("Boktekst", boktekst, height=500)

        st.subheader("📥 Last ned boken:")
        st.download_button("📥 Last ned som TXT", open(txt_fil, "rb"), file_name=txt_fil)

        st.subheader("📢 SEO-optimalisert beskrivelse:")
        st.text_area("Beskrivelse og nøkkelord", metadata, height=150)

        st.subheader("📘 Generert Bokomslag:")
        st.image(omslag_fil, caption="Automatisk generert bokomslag")
    else:
        st.warning("Velg en nisje først.")
