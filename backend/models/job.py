from sqlalchemy import Column, Integer, String, Text
from ..database import Base


class Job(Base):
	__tablename__ = "jobs"

	id = Column(Integer, primary_key=True)
	job_id = Column(String(64), unique=True, nullable=False)
	title = Column(String(255), nullable=False)
	company = Column(String(255), nullable=False)
	location = Column(String(255), nullable=True)
	description = Column(Text, nullable=False)
	skills = Column(Text, nullable=True)  # semicolon-separated
