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

# 🔹 Funksjon for å generere fullstendige kapitler på riktig språk
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

# 🔹 Funksjon for å analysere og optimalisere bokens innhold
def analyser_og_juster_bok(boktekst, nisje, språk):
    prompt = f"""
    Evaluer denne teksten opp mot bestselgende bøker innen {nisje} på Amazon KDP. 
    Gi en score fra 1-100 basert på:
    - Lesbarhet
    - Engasjement
    - SEO-optimalisering
    - Kommersiell appell
    
    Deretter foreslå konkrete forbedringer og generer en optimalisert versjon av teksten. 
    Skriv på {språk}.
    
    Tekst:
    {boktekst}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# 🔹 Funksjon for å generere et bokomslag tilpasset formål og målgruppe
def generer_omslag(tittel, kategori):
    prompt = f"""
    Lag et profesjonelt bokomslag for boken '{tittel}', optimalisert for Amazon KDP. 
    Designet bør være visuelt tiltalende for målgruppen til {kategori}-bøker. 
    Inkluder farger, typografi og designstil som appellerer til lesere i denne nisjen.
    """
    
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

# 🔹 Funksjon for å lage en nedlastbar tekstfil
def lag_txt(boktittel, bokinnhold):
    filnavn = f"{boktittel}.txt"
    with open(filnavn, "w", encoding="utf-8") as f:
        f.write(bokinnhold)
    return filnavn

# 🔹 Streamlit-app
st.title("📖 AI Bestselger-Bokgenerator for Amazon KDP")

ekspertmodus = st.checkbox("Ekspertmodus: Aktiver alle optimaliseringsverktøy")
analysemodus = st.checkbox("Analysemodus: Evaluer og optimaliser bokens innhold")

språk = st.selectbox("Velg språk for boken:", list(språkvalg.keys()))
kategori = st.selectbox("Velg en bestselgende kategori:", ["Velg en kategori..."] + bestseller_nisjer)
antall_kapitler = st.slider("Velg antall kapitler", min_value=3, max_value=10, value=5)

if st.button("Generer Bok"):
    st.info("Genererer boken, vennligst vent...")
    valgt_språk = språkvalg[språk]
    
    boktekst = generer_bok(kategori, antall_kapitler, valgt_språk)
    txt_fil = lag_txt(kategori, boktekst)

    st.subheader("📖 Din Genererte Bok:")
    st.text_area("Boktekst", boktekst, height=500)
    st.download_button("📥 Last ned som TXT", open(txt_fil, "rb"), file_name=txt_fil)

    if analysemodus:
        st.subheader("📊 Optimalisert bokinnhold basert på analyse:")
        optimalisert_tekst = analyser_og_juster_bok(boktekst, kategori, valgt_språk)
        st.text_area("Optimalisert Boktekst", optimalisert_tekst, height=500)

    st.subheader("📘 Generert Bokomslag:")
    omslag_fil = generer_omslag(kategori, kategori)
    st.image(omslag_fil, caption="Amazon KDP-optimalisert bokomslag")
