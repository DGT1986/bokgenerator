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
    "Engelsk": "English",
    "Spansk": "Spanish",
    "Tysk": "German",
    "Fransk": "French",
    "Italiensk": "Italian",
    "Norsk": "Norwegian",
    "Nederlandsk": "Dutch",
    "Portugisisk": "Portuguese"
}

# 🔹 Funksjon for å generere fullstendige kapitler på riktig språk
def generer_bok(nisje, antall_kapitler, språk):
    system_prompt = f"You are a professional book writer. Always respond in {språk}. Do not use any other language."

    kapittel_prompt = f"Generate a chapter outline for a best-selling book about {nisje} with {antall_kapitler} chapters. Respond only in {språk}."
    
    kapittel_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": kapittel_prompt}
        ],
        temperature=0.7
    )
    
    kapitler = kapittel_response.choices[0].message.content.split("\n")

    bok_tekst = f"# {nisje} - AI-generated book ({språk})\n\n"
    
    for i, kapittel in enumerate(kapitler[:antall_kapitler]):
        if kapittel.strip():
            kapittel_prompt = f"""
            Write a detailed chapter titled '{kapittel}' for a best-selling book about {nisje}.
            Include actionable tips, examples, and practical exercises.
            Write in an engaging and easy-to-read style.  
            **Respond only in {språk}.**
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
            bok_tekst += f"## Chapter {i+1}: {kapittel}\n\n{kapittel_tekst}\n\n"

    return bok_tekst

# 🔹 Funksjon for å analysere og optimalisere bokens innhold
def analyser_og_juster_bok(boktekst, nisje, språk):
    prompt = f"""
    Evaluate this text compared to best-selling books in {nisje} on Amazon KDP.
    Give a score from 1-100 based on:
    - Readability
    - Engagement
    - SEO optimization
    - Commercial appeal

    Then suggest concrete improvements and generate an optimized version of the text.
    **Respond only in {språk}.**

    Text:
    {boktekst}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are an expert in book writing. Always respond in {språk}."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# 🔹 Funksjon for å lagre bokteksten og holde den synlig etter nedlasting
def lag_txt(boktittel, bokinnhold):
    filnavn = f"{boktittel}.txt"
    st.session_state["last_generated_text"] = bokinnhold  # Holder teksten synlig
    return BytesIO(bokinnhold.encode("utf-8")), filnavn

# 🔹 Streamlit-app
st.title("📖 AI Bestseller Book Generator for Amazon KDP")

ekspertmodus = st.checkbox("Expert Mode: Activate all optimization tools")
analysemodus = st.checkbox("Analysis Mode: Evaluate and optimize book content")

språk = st.selectbox("Select the language for your book:", list(språkvalg.keys()))
kategori = st.selectbox("Select a best-selling category:", ["Select a category..."] + bestseller_nisjer)
antall_kapitler = st.slider("Select the number of chapters", min_value=3, max_value=10, value=5)

if st.button("Generate Book"):
    st.info("Generating book, please wait...")
    valgt_språk = språkvalg[språk]
    
    boktekst = generer_bok(kategori, antall_kapitler, valgt_språk)
    txt_buffer, txt_filnavn = lag_txt(kategori, boktekst)

    st.session_state["generated_text"] = boktekst  # Keeps text visible after download

# 📖 Display book text if it was generated
if "generated_text" in st.session_state:
    st.subheader("📖 Your Generated Book:")
    st.text_area("Book Text", st.session_state["generated_text"], height=500)

    # 📥 Download button that does not reset the app
    st.download_button("📥 Download as TXT", txt_buffer, file_name=txt_filnavn, mime="text/plain")

# 📊 Analysis Mode – keeps visible after download
if analysemodus and "generated_text" in st.session_state:
    st.subheader("📊 Book Sales Potential Analysis:")
    analyse_resultat = analyser_og_juster_bok(st.session_state["generated_text"], kategori, valgt_språk)
    st.text_area("Analysis and Improvements", analyse_resultat, height=200)
