# Job Recommendation

This folder is reserved for a job recommendation module/project.

Contents will be added here. Let me know what you want included (e.g., data ingestion, feature engineering, model training, API/GUI).
## AI Powered Job Recommendation System

Find relevant jobs from your resume using TF‑IDF and skills matching. Includes:
- Streamlit UI to upload/paste resume and view ranked jobs
- Flask API with endpoints for jobs, users, and recommendations
- SQLite by default (no setup), optional Postgres via DATABASE_URL
- Simple CSV seeding and skills dictionary

## Features
- Resume parsing for PDF/DOCX/TXT
- Hybrid scoring: TF‑IDF similarity + skills overlap (tunable weights)
- Toggle: local ranking (CSV) or backend API ranking
- Helpful company links (official/careers/site search)
- Sample dataset included (`data/jobs_sample.csv`)

## Project Structure
app/ # Streamlit UI + recommendation logic
parser.py # PDF/DOCX/TXT parsing
processing.py # Text normalization + NLTK
recommender.py # TF-IDF + skills ranking
ui_app.py # Streamlit app
backend/ # Flask API
app.py # create_app()
database.py # SQLAlchemy + SQLite default
models/ # Job, User
routes/ # /api/jobs, /api/users, /api/match
services/ # NLP utilities
seed.py # Seed DB from CSV
data/ # Sample jobs + skills list


