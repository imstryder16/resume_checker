import streamlit as st
import PyPDF2
import re
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

    #TECH / DATA
    "python", "python programming", "coding in python",
    "sql", "database", "database management",
    "excel", "advanced excel", "spreadsheets",
    "data analysis", "analyzed data", "data-driven",
    "machine learning", "ml models", "predictive modeling",
    "automation", "process automation",
    "tensorflow", "pandas", "numpy",

    #BUSINESS / MANAGEMENT
    "leadership", "led a team", "team leader",
    "teamwork", "collaborated with others", "cross-functional team",
    "communication", "strong communication", "presented findings",
    "project management", "managed projects", "project coordination",
    "strategy", "strategic planning",
    "problem solving", "solved problems", "critical thinking",
    "time management", "meeting deadlines",
    "organization", "organizational skills",

    #SALES / MARKETING
    "sales", "sales experience", "customer acquisition",
    "marketing", "digital marketing", "social media marketing",
    "content creation", "created content", "branding",
    "customer service", "client support", "helped customers",
    "negotiation", "persuasion", "client relations",

    #FINANCE / ADMIN
    "budgeting", "managed budgets", "financial planning",
    "accounting", "bookkeeping",
    "forecasting", "financial forecasting",
    "reporting", "prepared reports",
    "attention to detail", "detail-oriented",

    #HEALTHCARE
    "patient care", "cared for patients",
    "medical terminology", "clinical knowledge",
    "empathy", "patient support",
    "healthcare experience", "medical experience",

    #EDUCATION
    "teaching", "taught students", "instruction",
    "curriculum development", "lesson planning",
    "mentoring", "guided students",
    "training", "staff training",

    #CREATIVE / MEDIA
    "creativity", "creative thinking",
    "design", "graphic design", "visual design",
    "writing", "content writing", "copywriting",
    "editing", "proofreading",
    "social media", "instagram management", "tiktok content",

    #GENERAL SOFT SKILLS
    "adaptability", "adapted quickly",
    "collaboration", "worked with teams",
    "initiative", "took initiative",
    "work ethic", "strong work ethic"
]

def extract_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS_DB:
        if skill in text:
            found.append(skill)

    return list(set(found))
    
def get_missing_skills(resume_text, job_desc):
    resume_words = set(resume_text.lower().split())
    job_words = set(job_desc.lower().split())
    missing = job_words - resume_words
    return list(missing)[:20]

def calculate_score(found_skills, job_desc):
    job_desc = job_desc.lower()

    # find skills mentioned in job description
    required_skills = [skill for skill in SKILLS_DB if skill in job_desc]

    if len(required_skills) == 0:
        return 60  # neutral score if job description is unclear

    matched = set(found_skills).intersection(set(required_skills))

    score = (len(matched) / len(required_skills)) * 100

    # soften extremes so it feels realistic
    if score == 0:
        score = 15
    elif score < 30:
        score += 10

    return int(min(score, 100))

# -----------------------------
# 🤖 AI FEEDBACK
# -----------------------------
import random

def generate_ai_feedback(resume_text):
    text = resume_text.lower()

    strengths = []
    weaknesses = []
    improvements = []

    # -----------------------------
    # CORE SKILL SIGNALS
    # -----------------------------

    # TECH
    if any(word in text for word in ["python", "sql", "data", "machine learning"]):
        strengths.append("Demonstrates technical proficiency in data or programming-related skills, which are highly valuable in analytical roles.")
    else:
        weaknesses.append("Limited evidence of technical or analytical skills such as programming or data analysis.")
        improvements.append("Consider adding technical tools, data analysis experience, or software skills relevant to your target field.")

    # BUSINESS / MANAGEMENT
    if any(word in text for word in ["lead", "managed", "team", "project"]):
        strengths.append("Shows experience in leadership or project involvement, indicating responsibility and initiative.")
    else:
        improvements.append("Include examples of leadership, teamwork, or project coordination to strengthen managerial appeal.")

    # COMMUNICATION
    if any(word in text for word in ["communication", "presented", "client", "customer"]):
        strengths.append("Highlights strong communication or client interaction skills, which are essential in most professional roles.")
    else:
        improvements.append("Add examples of communication, presentations, or client interaction to improve interpersonal skill visibility.")

    # CREATIVE / MARKETING
    if any(word in text for word in ["design", "content", "marketing", "social media"]):
        strengths.append("Includes creative or marketing-related experience, showing versatility and audience awareness.")
    else:
        improvements.append("Consider adding creative, writing, or marketing experience depending on your career goals.")

    # EDUCATION / TRAINING
    if any(word in text for word in ["taught", "training", "mentored", "education"]):
        strengths.append("Demonstrates teaching or mentoring experience, which reflects leadership and communication ability.")
    else:
        improvements.append("If applicable, include mentoring or training experience to show knowledge transfer skills.")

    # GENERAL QUALITY CHECK
    if len(text) < 400:
        weaknesses.append("Resume appears brief and may lack sufficient detail.")
        improvements.append("Expand bullet points with measurable achievements and specific outcomes.")

    if "achievement" not in text and "result" not in text and "increased" not in text:
        improvements.append("Add quantifiable achievements (e.g., improved efficiency by 20%) to strengthen impact.")

    # -----------------------------
    # DIVERSITY LAYER (VARIED OUTPUT)
    # -----------------------------

    extra_strengths = [
        "The resume shows transferable skills that can apply across multiple industries.",
        "There is evidence of adaptability and willingness to learn new tools or environments.",
        "The structure suggests a developing but promising professional profile."
    ]

    extra_improvements = [
        "Tailor your resume more specifically to the job description for better alignment.",
        "Use stronger action verbs like 'developed', 'led', or 'implemented' to increase impact.",
        "Ensure each experience includes clear outcomes or measurable results.",
        "Improve keyword alignment with industry-specific requirements."
    ]

    strengths += random.sample(extra_strengths, 1)
    improvements += random.sample(extra_improvements, 2)

    # -----------------------------
    # FORMAT OUTPUT
    # -----------------------------

    def format_list(items):
        return "\n".join([f"- {item}" for item in items]) if items else "- None identified"

    return f"""
📊 AI RESUME ANALYSIS
-----------------------------------

🟢 STRENGTHS:
{format_list(strengths)}

🔴 WEAKNESSES:
{format_list(weaknesses)}

🟡 SUGGESTED IMPROVEMENTS:
{format_list(improvements)}

-----------------------------------
Overall Insight:
This resume demonstrates a developing professional profile. With more specific achievements, stronger keyword alignment, and clearer impact statements, it can be significantly improved for competitive job applications.
"""
# -----------------------------
# Streamlit UI
# -----------------------------

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("Resume Analyzer")
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
st.write("Built with Streamlit")
