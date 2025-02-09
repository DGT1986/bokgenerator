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
    
    kapitler = [k.strip() for k in kapittel_response.choices[0].message.content.split("\n") if k.strip()]

    bok_tekst = f"Title: {nisje} - A Self-Help Guide\n\n"

    for i, kapittel in enumerate(kapitler[:antall_kapitler]):
        kapittel_nummer = i + 1
        kapittel_prompt = f"""
        Write Chapter {kapittel_nummer} titled '{kapittel}' for a best-selling book about {nisje}.
        - The chapter should include a clear introduction, actionable tips, and practical exercises.
        - Each section should have an engaging heading.
        - Avoid repeating "Chapter X" inside the chapter text.
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
        bok_tekst += f"Chapter {kapittel_nummer}: {kapittel}\n\n{kapittel_tekst}\n\n"

    return bok_tekst

# 🔹 Funksjon for å generere bokomslag
def generer_omslag(tittel, kategori):
    prompt = f"""
    Create a professional book cover for '{tittel}', optimized for Amazon KDP.
    The design should match the target audience of {kategori} books.
    Include colors, typography, and a style that appeals to readers in this niche.
    """
    
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    
    if response and "data" in response:
        image_url = response["data"][0]["url"]
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        filnavn = f"{tittel}_cover.jpg"
        image.save(filnavn)
        return filnavn
    else:
        return None

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

    # 📘 Generate and store book cover
    omslag_fil = generer_omslag(kategori, kategori)
    st.session_state["generated_cover"] = omslag_fil if omslag_fil else "No cover generated."

# 📖 Display book text if it was generated
if "generated_text" in st.session_state:
    st.subheader("📖 Your Generated Book:")
    st.text_area("Book Text", st.session_state["generated_text"], height=500)

    # 📥 Download button that does not reset the app
    st.download_button("📥 Download as TXT", txt_buffer, file_name=txt_filnavn, mime="text/plain")

# 📘 Show book cover if generated
if "generated_cover" in st.session_state and st.session_state["generated_cover"] != "No cover generated.":
    st.subheader("📘 Generated Book Cover:")
    st.image(st.session_state["generated_cover"], caption="Amazon KDP-optimized book cover")

# 📊 Analysis Mode – keeps visible after download
if analysemodus and "generated_text" in st.session_state:
    st.subheader("📊 Book Sales Potential Analysis:")
    analyse_resultat = analyser_og_juster_bok(st.session_state["generated_text"], kategori, valgt_språk)
    st.text_area("Analysis and Improvements", analyse_resultat, height=200)
