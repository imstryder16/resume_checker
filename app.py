import streamlit as st
import PyPDF2
import re
import requests
import os

# -----------------------------
# Helper Functions
# -----------------------------

def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def clean_text(text):
    return re.sub(r'\s+', ' ', text)

SKILLS_DB = [
    "python", "java", "c++", "sql", "excel", "machine learning",
    "data analysis", "communication", "leadership", "project management",
    "tensorflow", "pandas", "numpy", "powerpoint"
]

def extract_skills(text):
    text = text.lower()
    found = []
    for skill in SKILLS_DB:
        if skill in text:
            found.append(skill)
    return found

def get_missing_skills(resume_text, job_desc):
    resume_words = set(resume_text.lower().split())
    job_words = set(job_desc.lower().split())
    missing = job_words - resume_words
    return list(missing)[:20]

def calculate_score(found_skills, job_desc):
    job_words = set(job_desc.lower().split())
    if len(job_words) == 0:
        return 0
    matched = len([word for word in found_skills if word in job_words])
    return int((matched / len(job_words)) * 100)

# -----------------------------
# 🤖 GEMINI AI FEEDBACK
# -----------------------------
def generate_ai_feedback(resume_text):
    try:
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

        headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
        }

        payload = {
            "inputs": f"""
You are a professional resume reviewer.

Analyze this resume and provide:
- Strengths
- Weaknesses
- Improvements

Resume:
{resume_text}
"""
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        return response.json()[0]["generated_text"]

    except Exception as e:
        return f"Error generating feedback: {e}"
# -----------------------------
# Streamlit UI
# -----------------------------

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("📄 AI Resume Analyzer (Gemini Powered)")
st.write("Upload your resume and compare it with a job description.")

uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
job_desc = st.text_area("Paste Job Description Here")

if uploaded_file is not None:
    with st.spinner("Reading your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_text = clean_text(resume_text)

    st.subheader("📄 Resume Preview")
    st.write(resume_text[:1000] + "...")

    found_skills = extract_skills(resume_text)

    st.subheader("✅ Skills Found")
    if found_skills:
        st.success(", ".join(found_skills))
    else:
        st.warning("No matching skills found.")

    if job_desc:
        missing = get_missing_skills(resume_text, job_desc)
        score = calculate_score(found_skills, job_desc)

        st.subheader("📊 Resume Score")
        st.metric(label="Match Score", value=f"{score}%")

        st.subheader("⚠️ Missing Keywords")
        st.write(", ".join(missing))

        st.subheader("🤖 AI Feedback")
        with st.spinner("Generating AI feedback..."):
            feedback = generate_ai_feedback(resume_text)
        st.write(feedback)

else:
    st.info("Please upload a PDF resume to begin.")

st.write("---")
st.write("Built with Streamlit + Google Gemini")
