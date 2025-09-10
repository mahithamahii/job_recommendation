from pathlib import Path
from flask import Blueprint, request

from ..database import session_scope
from ..models.job import Job
from ..models.user import User
from ..services.recommender import RecommenderService


match_bp = Blueprint("match", __name__)


@match_bp.post("/")
def match_jobs():
	data = request.get_json(force=True)
	resume_text = data.get("resume_text")
	user_id = data.get("user_id")
	weight_tfidf = float(data.get("weight_tfidf", 0.7))
	weight_skills = float(data.get("weight_skills", 0.3))
	top_k = int(data.get("top_k", 10))

	with session_scope() as s:
		if not resume_text and user_id:
			user = s.get(User, int(user_id))
			if not user:
				return {"error": "user not found"}, 404
			resume_text = user.resume_text or ""

		jobs = s.query(Job).all()
		skills_master = []
		rec = RecommenderService(jobs, skills_master)
		ranked = rec.rank(resume_text or "", weight_tfidf=weight_tfidf, weight_skills=weight_skills, top_k=top_k)

		return {
			"items": [
				{
					"id": r.job.id,
					"job_id": r.job.job_id,
					"title": r.job.title,
					"company": r.job.company,
					"location": r.job.location,
					"skills": r.job.skills,
					"score": r.score,
				}
				for r in ranked
			]
		}
