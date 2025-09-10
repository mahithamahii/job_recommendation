from flask import Flask
from flask_cors import CORS
from .database import init_engine_and_session


def create_app() -> Flask:
	app = Flask(__name__)
	CORS(app)

	# Database
	init_engine_and_session()

	# Blueprints
	from .routes.jobs import jobs_bp
	from .routes.users import users_bp
	from .routes.match import match_bp

	app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
	app.register_blueprint(users_bp, url_prefix="/api/users")
	app.register_blueprint(match_bp, url_prefix="/api/match")

	@app.get("/api/health")
	def health():
		return {"status": "ok"}

	return app
