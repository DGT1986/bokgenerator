import openai
import os
import streamlit as st

# Sett API-nøkkelen som miljøvariabel
openai.api_key = os.getenv("OPENAI_API_KEY")

# Funksjon for å generere bokkapitler
def generer_kapitler(emne):
    prompt = f"Lag en kapitteloversikt for en bok om emnet: {emne}. Fokuser på 'how-to' stil."
response = openai.client.chat.completions.create(        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du er en ekspert på bokskriving."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# Funksjon for nøkkelord-analyse
def generer_nokkelord(emne):
    prompt = f"Hvilke nøkkelord og kategorier er best for en bok om {emne} på Amazon KDP?"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du er en markedsføringsassistent for selvpublisering."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# Streamlit-app for grensesnitt
st.title("Bokgenerator for Passiv Inntekt")

emne = st.text_input("Skriv inn emnet for boken din:")

if st.button("Generer Kapitteloversikt"):
    if emne:
        kapitler = generer_kapitler(emne)
        st.subheader("Kapitteloversikt:")
        st.write(kapitler)  # Bedre formatering
    else:
        st.warning("Vennligst skriv inn et emne først.")

if st.button("Få Nøkkelordforslag"):
    if emne:
        nokkelord = generer_nokkelord(emne)
        st.subheader("Nøkkelord:")
        st.write(nokkelord)  # Bedre formatering
    else:
        st.warning("Vennligst skriv inn et emne først.")
