from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st

# Ensure project root is on sys.path so 'app' package is importable when run via Streamlit
import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from app.parser import read_text_from_bytes
from app.recommender import JobRecommender
import requests


st.set_page_config(page_title="AI Powered Job Recommendation System", page_icon="🧭", layout="wide")
st.title("AI Powered Job Recommendation System")

BASE_DIR = Path(__file__).resolve().parents[1]
JOBS_CSV = BASE_DIR / "data" / "jobs_sample.csv"
SKILLS_PATH = BASE_DIR / "data" / "skills_master.txt"


@st.cache_resource(show_spinner=False)
def load_recommender() -> JobRecommender:
    return JobRecommender(JOBS_CSV, SKILLS_PATH)


rec = load_recommender()

st.sidebar.header("Input")
uploaded = st.sidebar.file_uploader("Upload resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
tfidf_weight = st.sidebar.slider("TF-IDF weight", 0.0, 1.0, 0.7, 0.05)
skills_weight = 1.0 - tfidf_weight
top_k = st.sidebar.slider("Top K", 3, 30, 10, 1)
use_backend = st.sidebar.toggle("Use backend API", value=False, help="Call Flask /api/match instead of local ranking")
backend_url = st.sidebar.text_input("Backend URL", value="http://127.0.0.1:5000", help="Root of the Flask API")

resume_text = ""
if uploaded is not None:
    resume_text = read_text_from_bytes(uploaded.name, uploaded.read())
    with st.expander("Extracted Resume Text", expanded=False):
        st.write(resume_text[:5000] + ("..." if len(resume_text) > 5000 else ""))
else:
    st.info("Upload a resume to get recommendations. Or paste text below.")

resume_text = st.text_area("Or paste resume text", value=resume_text, height=220)

if st.button("Recommend Jobs", type="primary"):
    if not resume_text.strip():
        st.warning("Please upload or paste resume text.")
    else:
        with st.spinner("Scoring jobs..."):
            if use_backend:
                try:
                    resp = requests.post(
                        f"{backend_url.rstrip('/')}/api/match/",
                        json={
                            "resume_text": resume_text,
                            "weight_tfidf": tfidf_weight,
                            "weight_skills": skills_weight,
                            "top_k": top_k,
                        },
                        timeout=60,
                    )
                    resp.raise_for_status()
                    items = resp.json().get("items", [])
                    if not items:
                        st.info("No results from backend.")
                        df = pd.DataFrame()
                    else:
                        df = pd.DataFrame(items)
                except Exception as e:
                    st.error(f"Backend error: {e}")
                    df = pd.DataFrame()
            else:
                df = rec.recommend(
                    resume_text, top_k=top_k, weight_tfidf=tfidf_weight, weight_skills=skills_weight
                )
        st.success(f"Top {len(df)} recommendations")
        st.dataframe(
            df[["job_id", "title", "company", "location", "score", "skills"]],
            use_container_width=True,
            hide_index=True,
        )
        with st.expander("Show details"):
            for _, row in df.iterrows():
                st.markdown(f"### {row['title']} — {row['company']} ({row['location']})")
                st.markdown(f"**Score**: {row['score']:.3f}")
                st.markdown(f"**Skills**: {row['skills']}")
                # Helpful links
                q = quote(f"{row['title']} {row['company']} careers {row['location']}")
                q_company = quote(f"{row['company']} official site")
                q_careers = quote(f"{row['company']} careers site")
                q_linkedin = quote(f"{row['company']}")
                q_glassdoor = quote(f"{row['company']}")
                q_indeed = quote(f"{row['company']}")

                # Build only official/first-party oriented links
                company_slug = ''.join(ch for ch in str(row['company']).lower() if ch.isalnum())
                guessed_domain = f"{company_slug}.com"
                site_q = quote(f"site:{guessed_domain} (careers OR jobs)")

                links = [
                    ("Official careers (Google)", 'https://www.google.com/search?q=' + q_careers),
                    ("Company site (Google)", 'https://www.google.com/search?q=' + q_company),
                    ("Site search (company domain)", 'https://www.google.com/search?q=' + site_q),
                ]
                st.markdown(" · ".join([f"[{name}]({url})" for name, url in links]))
                st.markdown("**Description**:")
                st.write(row["description"])



