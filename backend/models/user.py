from sqlalchemy import Column, Integer, String, Text, Enum
from ..database import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	email = Column(String(255), unique=True, nullable=False)
	name = Column(String(255), nullable=False)
	role = Column(Enum("candidate", "employer", name="user_roles"), nullable=False)
	resume_text = Column(Text, nullable=True)
