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

# 🔹 Definer listen over bestselgende Amazon KDP-kategorier HER før den brukes
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

# Streamlit-app
st.title("📖 AI Bestselger-Bokgenerator med Optimaliseringsmotor")

# 🔹 Nå kan du bruke `bestseller_nisjer` i `st.selectbox()`
kategori = st.selectbox("Velg en bestselgende kategori:", ["Velg en kategori..."] + bestseller_nisjer)
