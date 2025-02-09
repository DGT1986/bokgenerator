import openai
import os
import streamlit as st
import requests
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
    system_prompt = f"Du er en profesjonell forfatter. Svar KUN på {språk}. Ikke bruk noe annet språk."
    
    kapittel_prompt = f"Generer en kapitteloversikt for en bestselgende bok om {nisje} med {antall_kapitler} kapitler. Svar kun på {språk}."
    
    kapittel_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": kapittel_prompt}
        ],
        temperature=0.7
    )
    
    kapitler = kapittel_response.choices[0].message.content.split("\n")

    bok_tekst = f"# {nisje} - AI-generert bok ({språk})\n\n"
    
    for i, kapittel in enumerate(kapitler[:antall_kapitler]):
        if kapittel.strip():
            kapittel_prompt = f"""
            Skriv et detaljert kapittel med tittelen '{kapittel}' for en bestselgende bok om {nisje}. 
            Inkluder actionable tips, eksempler og praktiske øvelser. 
            Skriv i en engasjerende og lettlest stil.  
            **Svar kun på {språk}.**
            """
            
            kapittel_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": kapittel_prompt}
                ],
                temperature=0.7
            )
            
            kapittel_tekst = kapittel_response.choices[0].message.content
            bok_tekst += f"## Kapittel {i+1}: {kapittel}\n\n{kapittel_tekst}\n\n"

    return bok_tekst

# 🔹 Funksjon for å lagre bokteksten i session state og generere en nedlastbar tekstfil
def lag_txt(boktittel, bokinnhold):
    filnavn = f"{boktittel}.txt"
    st.session_state["last_generated_text"] = bokinnhold  # Lagrer teksten slik at den forblir synlig
    return BytesIO(bokinnhold.encode("utf-8")), filnavn

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
    txt_buffer, txt_filnavn = lag_txt(kategori, boktekst)

    st.session_state["generated_text"] = boktekst  # Holder teksten synlig selv etter nedlasting

# 📖 Vis boktekst hvis den er generert tidligere
if "generated_text" in st.session_state:
    st.subheader("📖 Din Genererte Bok:")
    st.text_area("Boktekst", st.session_state["generated_text"], height=500)

    # 📥 Nedlastingsknapp – Bruker buffer for å unngå reset av appen
    st.download_button("📥 Last ned som TXT", txt_buffer, file_name=txt_filnavn, mime="text/plain")

# 📊 Analysemodus – behold synlig etter nedlasting
if analysemodus and "generated_text" in st.session_state:
    st.subheader("📊 Analyse av bokens salgspotensial:")
    analyse_resultat = analyser_og_juster_bok(st.session_state["generated_text"], kategori, valgt_språk)
    st.text_area("Analyse og forbedringer", analyse_resultat, height=200)
