import os
import streamlit as st
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv

# 1. Load your secret Gemini API key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Set up the page title and layout
st.set_page_config(page_title="AI Study Buddy", page_icon="📚", layout="centered")
st.title("📚 AI Study Buddy (Notes to Quiz)")
st.write("Paste your notes or upload a PDF chapter to generate a quick revision pack.")

# 3. Take Input from the User (Paste Text or Upload PDF)
choice = st.radio("Select input type:", ["Paste Notes", "Upload PDF"])

study_notes = ""

if choice == "Paste Notes":
    study_notes = st.text_area(
        "Paste your notes or chapter text below:",
        height=200,
        placeholder="Paste a paragraph from your textbook or lecture notes here..."
    )
else:
    uploaded_pdf = st.file_uploader("Upload your notes (PDF)", type=["pdf"])
    if uploaded_pdf is not None:
        reader = PdfReader(uploaded_pdf)
        for page in reader.pages:
            study_notes += page.extract_text() or ""
        st.info(f"PDF loaded! Extracted text from {len(reader.pages)} page(s).")

# 4. Send to Gemini AI when button is clicked
if st.button("Create Revision Pack ✨", type="primary"):
    if not api_key:
        st.error("API key not found. Check your .env file.")
    elif not study_notes.strip():
        st.warning("Please paste some notes or upload a PDF first.")
    else:
        with st.spinner("Generating summary, quiz, and key terms..."):
            try:
                prompt = f"""
                You are a helpful study tutor. Convert the following study notes into a quick revision pack.

                STUDY NOTES:
                {study_notes}

                Format your response strictly like this:

                ### 📌 Summary (5–6 Bullet Points)
                * ...

                ### 📝 5 Multiple-Choice Questions
                **Q1.** [Question]
                - A) ...
                - B) ...
                - C) ...
                - D) ...
                **Answer:** [Correct option and 1-sentence reason]

                *(Continue for Q2, Q3, Q4, Q5)*

                ### 🔑 3 Key Terms & Simple Meanings
                1. **[Term 1]:** [Simple 1-sentence meaning]
                2. **[Term 2]:** [Simple 1-sentence meaning]
                3. **[Term 3]:** [Simple 1-sentence meaning]
                """

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                )

                # 5. Show the Output clearly on screen
                st.success("Revision Pack Ready!")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Something went wrong: {e}")