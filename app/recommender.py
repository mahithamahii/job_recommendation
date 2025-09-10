from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple

import numpy as np
import pandas as pd
from rapidfuzz.fuzz import ratio as fuzz_ratio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .processing import extract_skills, load_skills_master, normalize_text


@dataclass
class JobRecord:
    job_id: str
    title: str
    company: str
    location: str
    description: str
    skills: List[str]


class JobRecommender:
    def __init__(self, jobs_csv: Path, skills_path: Path):
        self.jobs_df = self._load_jobs(jobs_csv)
        self.skills_master = load_skills_master(skills_path)
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_features=50000,
        )
        self.job_corpus = self.jobs_df["description_norm"].tolist()
        self.job_tfidf = self.vectorizer.fit_transform(self.job_corpus)

    @staticmethod
    def _load_jobs(path: Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        expected_cols = {"job_id", "title", "company", "location", "description", "skills"}
        missing = expected_cols - set(df.columns)
        if missing:
            raise ValueError(f"Jobs CSV missing columns: {missing}")
        df["description_norm"] = df["description"].fillna("").astype(str).map(normalize_text)
        df["skills_list"] = (
            df["skills"].fillna("")
            .astype(str)
            .map(lambda s: [t.strip() for t in s.split(";") if t.strip()])
        )
        return df

    def _skills_overlap(self, resume_skills: Set[str], job_skills: Sequence[str]) -> float:
        if not resume_skills or not job_skills:
            return 0.0
        # compute fuzzy overlap: if a resume skill is similar to any job skill > 85
        matched = 0
        for rs in resume_skills:
            for js in job_skills:
                if fuzz_ratio(rs.lower(), js.lower()) >= 85:
                    matched += 1
                    break
        denom = len(resume_skills.union(set(job_skills)))
        return matched / max(1, denom)

    def recommend(
        self,
        resume_text: str,
        top_k: int = 10,
        weight_tfidf: float = 0.7,
        weight_skills: float = 0.3,
    ) -> pd.DataFrame:
        text_norm = normalize_text(resume_text)
        resume_vec = self.vectorizer.transform([text_norm])
        sim = cosine_similarity(resume_vec, self.job_tfidf).ravel()

        resume_skills = extract_skills(text_norm, self.skills_master)
        skills_scores = np.array([
            self._skills_overlap(resume_skills, skills) for skills in self.jobs_df["skills_list"]
        ])

        score = weight_tfidf * sim + weight_skills * skills_scores
        top_idx = np.argsort(-score)[:top_k]

        result = self.jobs_df.iloc[top_idx].copy()
        result["score"] = score[top_idx]
        result["resume_skills_matched"] = [
            ", ".join(sorted(extract_skills(";".join(skills), resume_skills))) if resume_skills else ""
            for skills in result["skills_list"]
        ]
        return result[[
            "job_id", "title", "company", "location", "score", "skills", "resume_skills_matched", "description"
        ]].sort_values("score", ascending=False)



