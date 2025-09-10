from flask import Blueprint, request
from ..database import session_scope
from ..models.user import User


users_bp = Blueprint("users", __name__)


@users_bp.post("/")
def create_user():
	data = request.get_json(force=True)
	with session_scope() as s:
		user = User(
			email=data.get("email"),
			name=data.get("name", ""),
			role=data.get("role", "candidate"),
			resume_text=data.get("resume_text"),
		)
		s.add(user)
		s.flush()
		return {"id": user.id}, 201


@users_bp.put("/<int:user_id>/resume")
def update_resume(user_id: int):
	data = request.get_json(force=True)
	with session_scope() as s:
		user = s.get(User, user_id)
		if not user:
			return {"error": "not found"}, 404
		user.resume_text = data.get("resume_text", "")
		return {"status": "updated"}
