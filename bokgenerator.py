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

def finn_bestselgende_kategorier():
    prompt = "Analyser Amazon KDP-trender og gi en liste over de 5 bestselgende bokkategoriene akkurat nå. Forklar hvorfor de selger godt."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.7)
    return response.choices[0].message.content

def foreslå_emner(kategori):
    prompt = f"Foreslå 5 spesifikke bokemner innen {kategori} som selger godt akkurat nå. Inkluder hvorfor de er populære."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.7)
    return response.choices[0].message.content

def generer_tittel_og_beskrivelse(nisje, språk):
    prompt = f"Generer en bestselgende boktittel og en SEO-optimalisert beskrivelse for en bok innen {nisje}, skrevet på {språk}."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.7)
    return response.choices[0].message.content

def generer_nøkkelord(nisje, språk):
    prompt = f"Generer en liste over de mest relevante Amazon KDP-søkeordene for en bok innen {nisje}, skrevet på {språk}."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.7)
    return response.choices[0].message.content

def foreslå_bokpris(nisje, språk):
    prompt = f"Analyser prisene på de bestselgende bøkene innen {nisje} på Amazon KDP og foreslå en optimal prisstrategi."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.7)
    return response.choices[0].message.content

def generer_call_to_action(nisje, språk):
    prompt = f"Generer en sterk Call-to-Action (CTA) for en bok innen {nisje} som oppfordrer leseren til videre handling."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.7)
    return response.choices[0].message.content

def generer_omslag(tittel, kategori):
    prompt = f"Lag et profesjonelt bokomslag for '{tittel}', optimalisert for Amazon KDP, innen kategorien {kategori}."
    response = client.images.generate(
        model="dall-e-3", prompt=prompt, size="1024x1024")
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))
    filnavn = f"{tittel}_omslag.jpg"
    image.save(filnavn)
    return filnavn

# 🔹 Streamlit-app
st.title("📖 AI Bestselger-Bokgenerator for Amazon KDP")

ekspertmodus = st.checkbox("Ekspertmodus: Aktiver alle optimaliseringsverktøy")

if st.button("Analyser Amazon KDP-markedet"):
    st.info("Henter trender...")
    beste_kategorier = finn_bestselgende_kategorier()
    st.subheader("🔥 Bestselgende KDP-kategorier:")
    st.text_area("Beste Kategorier", beste_kategorier, height=200)

språk = st.selectbox("Velg språk for boken:", list(språkvalg.keys()))
kategori = st.selectbox("Velg en bestselgende kategori:", ["Velg en kategori..."] + bestseller_nisjer)
antall_kapitler = st.slider("Velg antall kapitler", min_value=3, max_value=10, value=5)

if ekspertmodus:
    st.subheader("📌 Optimalisert Boktittel og Beskrivelse:")
    optimal_tittel = generer_tittel_og_beskrivelse(kategori, språkvalg[språk])
    st.text_area("Tittel og Beskrivelse", optimal_tittel, height=150)

    st.subheader("🔍 Beste nøkkelord:")
    nøkkelord = generer_nøkkelord(kategori, språkvalg[språk])
    st.text_area("Amazon KDP nøkkelord", nøkkelord, height=100)

    st.subheader("💰 Anbefalt bokpris:")
    prisstrategi = foreslå_bokpris(kategori, språkvalg[språk])
    st.text_area("Prisstrategi", prisstrategi, height=100)

    st.subheader("🎯 Call-to-Action for mersalg:")
    cta = generer_call_to_action(kategori, språkvalg[språk])
    st.text_area("Call-to-Action", cta, height=100)

if st.button("Generer Bok"):
    st.info("Genererer boken, vennligst vent...")
    boktekst = generer_tittel_og_beskrivelse(kategori, språkvalg[språk])
    txt_fil = f"{kategori}.txt"
    with open(txt_fil, "w", encoding="utf-8") as f:
        f.write(boktekst)

    st.subheader("📖 Din Genererte Bok:")
    st.text_area("Boktekst", boktekst, height=500)
    st.download_button("📥 Last ned som TXT", open(txt_fil, "rb"), file_name=txt_fil)

    omslag_fil = generer_omslag(kategori, kategori)
    st.subheader("📘 Generert Bokomslag:")
    st.image(omslag_fil, caption="Amazon KDP-optimalisert bokomslag")
