from pathlib import Path
import csv

from .database import init_engine_and_session, session_scope
from .models.job import Job


def seed_jobs_from_csv(csv_path: Path) -> None:
	init_engine_and_session()
	with session_scope() as s:
		with csv_path.open(newline="", encoding="utf-8") as f:
			reader = csv.DictReader(f)
			for row in reader:
				job = Job(
					job_id=row.get("job_id"),
					title=row.get("title"),
					company=row.get("company"),
					location=row.get("location"),
					description=row.get("description", ""),
					skills=row.get("skills", ""),
				)
				s.add(job)


if __name__ == "__main__":
	base = Path(__file__).resolve().parents[1]
	csv_file = base / "data" / "jobs_sample.csv"
	seed_jobs_from_csv(csv_file)
	print("Seeded jobs from", csv_file)


