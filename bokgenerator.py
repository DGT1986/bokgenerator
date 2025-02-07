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

# Funksjon for å analysere trender og anbefale bestselgende KDP-kategorier
def finn_bestselgende_kategorier():
    prompt = "Analyser Amazon KDP-trender og gi en liste over de 5 bestselgende bokkategoriene akkurat nå. Forklar hvorfor de selger godt."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Funksjon for å gi AI-anbefalte emner basert på KDP-trender
def foreslå_emner(kategori):
    prompt = f"Basert på den bestselgende KDP-kategorien '{kategori}', foreslå 5 spesifikke bokemner som er populære akkurat nå. Inkluder hvorfor de selger godt."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Funksjon for å generere en optimalisert boktittel og beskrivelse
def generer_tittel_og_beskrivelse(nisje):
    prompt = f"Generer en bestselgende boktittel og en kort beskrivelse for en bok innen nisjen {nisje}. Tittelen skal være engasjerende og optimalisert for Amazon KDP."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Funksjon for å generere et bokomslag med bedre KDP-optimalisering
def generer_omslag(tittel, kategori):
    prompt = f"Lag et profesjonelt bokomslag for boken '{tittel}'. Designet bør være optimalisert for Amazon KDP, med høy kontrast, lettlest font og en stil som passer til kategorien {kategori}."
    
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

# Funksjon for å generere bokinnhold basert på optimalisert emne
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
st.title("📖 AI Bestselger-Bokgenerator med Optimaliseringsmotor")

# Steg 1: Finn bestselgende kategorier
if st.button("Analyser Amazon KDP-markedet"):
    st.info("Henter trender...")
    beste_kategorier = finn_bestselgende_kategorier()
    st.subheader("🔥 Bestselgende KDP-kategorier:")
    st.text_area("Beste Kategorier", beste_kategorier, height=200)

# Steg 2: Velg en kategori
kategori = st.selectbox("Velg en bestselgende kategori:", ["Velg en kategori..."] + bestseller_nisjer)

# Steg 3: Foreslå spesifikke emner basert på valgt kategori
if kategori != "Velg en kategori...":
    foreslåtte_emner = foreslå_emner(kategori)
    st.subheader(f"📚 Populære emner innen {kategori}:")
    st.text_area("Forslåtte Emner", foreslåtte_emner, height=150)

# Steg 4: Generer boktittel og beskrivelse
if st.button("Generer boktittel og beskrivelse"):
    optimal_tittel = generer_tittel_og_beskrivelse(kategori)
    st.subheader("📌 Optimalisert Boktittel og Beskrivelse:")
    st.text_area("Tittel og Beskrivelse", optimal_tittel, height=150)

# Steg 5: Generer bokinnhold
antall_kapitler = st.slider("Velg antall kapitler", min_value=3, max_value=10, value=5)

if st.button("Generer Bok"):
    st.info("Genererer boken, vennligst vent...")
    boktekst = generer_bok(kategori, antall_kapitler)
    txt_fil = lag_txt(kategori, boktekst)

    st.subheader("📖 Din Genererte Bok:")
    st.text_area("Boktekst", boktekst, height=500)

    st.download_button("📥 Last ned som TXT", open(txt_fil, "rb"), file_name=txt_fil)

    omslag_fil = generer_omslag(kategori, kategori)
    st.subheader("📘 Generert Bokomslag:")
    st.image(omslag_fil, caption="Amazon KDP-optimalisert bokomslag")
