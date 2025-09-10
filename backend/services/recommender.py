from dataclasses import dataclass
from typing import List, Sequence, Set

import numpy as np
from rapidfuzz.fuzz import ratio as fuzz_ratio
from sklearn.metrics.pairwise import cosine_similarity

from ..models.job import Job
from .nlp import build_tfidf, extract_skills_spacy


@dataclass
class RankedJob:
	job: Job
	score: float


class RecommenderService:
	def __init__(self, jobs: Sequence[Job], skills_master: List[str]):
		self.jobs = list(jobs)
		self.skills_master = skills_master
		self.corpus = [j.description or "" for j in self.jobs]
		self.vectorizer = build_tfidf(self.corpus)
		self.job_tfidf = self.vectorizer.fit_transform(self.corpus)

	def _skills_overlap(self, resume_skills: Set[str], job_skills: List[str]) -> float:
		if not resume_skills or not job_skills:
			return 0.0
		matched = 0
		for rs in resume_skills:
			for js in job_skills:
				if fuzz_ratio(rs.lower(), js.lower()) >= 85:
					matched += 1
					break
		denom = len(resume_skills.union(set(job_skills)))
		return matched / max(1, denom)

	def rank(self, resume_text: str, weight_tfidf: float = 0.7, weight_skills: float = 0.3, top_k: int = 10) -> List[RankedJob]:
		resume_vec = self.vectorizer.transform([resume_text])
		tfidf_sim = cosine_similarity(resume_vec, self.job_tfidf).ravel()
		resume_skills = extract_skills_spacy(resume_text, self.skills_master)
		skill_scores = np.array([
			self._skills_overlap(resume_skills, (j.skills or "").split(";")) for j in self.jobs
		])
		score = weight_tfidf * tfidf_sim + weight_skills * skill_scores
		order = np.argsort(-score)[:top_k]
		return [RankedJob(self.jobs[i], float(score[i])) for i in order]
