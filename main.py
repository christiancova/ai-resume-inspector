from math import e
from openai.types import file_content
from openai.types.responses import response
import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Inspector 🕵🏼", page_icon="🕵🏼", layout="centered")
st.markdown("""
<style>

/* Main button (Spotify style) */
.stButton > button {
    background-color: #1DB954;
    color: black;
    font-weight: 600;
    border-radius: 25px;
    padding: 0.6em 1.4em;
    border: none;
    transition: 0.2s ease;
}

/* Hover effect */
.stButton > button:hover {
    background-color: #1ed760;
    transform: scale(1.02);
}

/* File uploader box */
section[data-testid="stFileUploader"] {
    background-color: #121212;
    border-radius: 12px;
    padding: 10px;
}

/* Text input styling */
input {
    background-color: #121212 !important;
    border-radius: 10px !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True) #name page/tab 

st.title("AI Resume Inspector")
st.markdown("Upload your resume and get personalized AI feedback to optimize it for recruiters and ATS systems.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Upload your resume (PFD or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the role you want your resume to be optimized for (optional)")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()

        prompt = f"""
You are an expert resume reviewer, recruiter, and ATS optimization specialist.

Task:
Analyze the resume below and provide constructive feedback tailored to the target role: 
"{job_role if job_role else "general"}"

Important constraint:
- The target role is only a HIGH-LEVEL title (e.g., "Software Engineer", "Data Analyst").
- Do NOT assume a specific company, seniority, tech stack, or job posting.
- When suggesting keywords, give a GENERAL role-relevant keyword list and clearly label them as "common keywords".

Focus on:
1) Overall Impact & Readability
- First impression, clarity, formatting, and professionalism
- Does it quickly communicate what the candidate does and their value?

2) Bullet Point Quality (Action + Impact)
- Identify vague bullets and rewrite them
- Encourage measurable outcomes (latency, cost, revenue, throughput, uptime, tickets resolved, etc.)
- Use strong action verbs and avoid repetition

3) Role Alignment (Title-level)
- What parts of the resume align well with "{job_role if job_role else "general"}"?
- What is missing or under-emphasized for this title?

4) Skills & Keywords (ATS-friendly)
- Review skills organization (categories, ordering, redundancy)
- Provide:
  a) "Skills to Highlight" (already present but should be emphasized)
  b) "Common Keywords to Consider" (general for this role)
- Mention ATS formatting risks (tables, icons, unusual columns, headers/footers)

5) Concrete Improvements
- Provide a prioritized list of improvements (top 5)
- Provide 3 rewritten bullet examples using the candidate’s existing content (do not invent fake experience)
- Suggest a stronger summary (1–2 versions) if needed

Resume:
-----------------------
{file_content}
-----------------------

Output format (use these headings):
**Overall Score (1–10)**
**Quick Summary**
**Strengths**
**Top 5 Improvements (Priority Order)**
**ATS & Formatting Checks**
**Skills Feedback**
- Skills to Highlight:
- Common Keywords to Consider:
**Rewritten Bullet Examples (3)**
**Optional: Improved Summary (1–2 versions)**
"""

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer with years of experience"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"An error ocurred: {str(e)}")

