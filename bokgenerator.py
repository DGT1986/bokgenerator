import openai
import os
import streamlit as st
from dotenv import load_dotenv

# Last inn API-nøkkel fra .env-fil
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Opprett OpenAI-klient
client = openai.Client(api_key=api_key)

# Funksjon for å generere bokkapitler
def generer_kapitler(emne):
    prompt = f"Lag en kapitteloversikt for en bok om emnet: {emne}. Fokuser på 'how-to' stil."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du er en ekspert på bokskriving."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Funksjon for nøkkelord-analyse
def generer_nokkelord(emne):
    prompt = f"Hvilke nøkkelord og kategorier er best for en bok om {emne} på Amazon KDP?"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du er en markedsføringsassistent for selvpublisering."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Streamlit-app for grensesnitt
st.title("Bokgenerator for Passiv Inntekt")

emne = st.text_input("Skriv inn emnet for boken din:")

if st.button("Generer Kapitteloversikt"):
    if emne:
        kapitler = generer_kapitler(emne)
        st.subheader("Kapitteloversikt:")
        st.write(kapitler)
    else:
        st.warning("Vennligst skriv inn et emne først.")

if st.button("Få Nøkkelordforslag"):
    if emne:
        nokkelord = generer_nokkelord(emne)
        st.subheader("Nøkkelord:")
        st.write(nokkelord)
    else:
        st.warning("Vennligst skriv inn et emne først.")
