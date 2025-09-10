from flask import Blueprint, request
from pathlib import Path
from ..database import session_scope
from ..models.job import Job
from ..seed import seed_jobs_from_csv


jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("/")
def list_jobs():
	page = int(request.args.get("page", 1))
	limit = int(request.args.get("limit", 20))
	offset = (page - 1) * limit
	with session_scope() as s:
		total = s.query(Job).count()
		items = s.query(Job).order_by(Job.id.desc()).offset(offset).limit(limit).all()
		return {
			"total": total,
			"page": page,
			"limit": limit,
			"items": [
				{
					"id": j.id,
					"job_id": j.job_id,
					"title": j.title,
					"company": j.company,
					"location": j.location,
					"skills": j.skills,
					"description": j.description,
				}
				for j in items
			],
		}


@jobs_bp.post("/")
def create_job():
	data = request.get_json(force=True)
	with session_scope() as s:
		job = Job(
			job_id=data.get("job_id"),
			title=data.get("title"),
			company=data.get("company"),
			location=data.get("location"),
			description=data.get("description", ""),
			skills=data.get("skills", ""),
		)
		s.add(job)
		s.flush()
		return {"id": job.id}, 201


@jobs_bp.post("/seed")
def seed_jobs():
	"""
	Seed jobs from a CSV file. Body: {"csv_path": "optional/path.csv"}
	Defaults to data/jobs_sample.csv at project root.
	"""
	data = request.get_json(silent=True) or {}
	csv_path = data.get("csv_path")
	if csv_path:
		csv_file = Path(csv_path)
	else:
		# backend/routes/ -> backend/ -> project root
		csv_file = Path(__file__).resolve().parents[2] / "data" / "jobs_sample.csv"
	if not csv_file.exists():
		return {"error": f"CSV not found: {csv_file}"}, 400
	seed_jobs_from_csv(csv_file)
	return {"status": "seeded", "csv": str(csv_file)}
