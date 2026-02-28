"""
Language learning app — Flask application factory.
"""
import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=Config):
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flask_app = Flask(
        __name__,
        template_folder=os.path.join(_root, "templates"),
        static_folder=os.path.join(_root, "static"),
        static_url_path="/static",
    )
    flask_app.config.from_object(config_class)

    CORS(flask_app)
    db.init_app(flask_app)
    jwt.init_app(flask_app)

    with flask_app.app_context():
        import app.models  # noqa: F401 - register models for create_all
        db.create_all()

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.categories import categories_bp
    from app.routes.reading import reading_bp
    from app.routes.listening import listening_bp
    from app.routes.writing import writing_bp
    from app.routes.speaking import speaking_bp
    from app.routes.reels import reels_bp
    from app.routes.tts_stt import tts_stt_bp
    from app.routes.feedback import feedback_bp
    from app.routes.pages import pages_bp

    flask_app.register_blueprint(pages_bp)
    flask_app.register_blueprint(auth_bp, url_prefix="/api/auth")
    flask_app.register_blueprint(users_bp, url_prefix="/api/users")
    flask_app.register_blueprint(categories_bp, url_prefix="/api/categories")
    flask_app.register_blueprint(reading_bp, url_prefix="/api/reading")
    flask_app.register_blueprint(listening_bp, url_prefix="/api/listening")
    flask_app.register_blueprint(writing_bp, url_prefix="/api/writing")
    flask_app.register_blueprint(speaking_bp, url_prefix="/api/speaking")
    flask_app.register_blueprint(reels_bp, url_prefix="/api/reels")
    flask_app.register_blueprint(tts_stt_bp, url_prefix="/api/tts-stt")
    flask_app.register_blueprint(feedback_bp, url_prefix="/api/feedback")

    @flask_app.route("/health")
    def health():
        return {"status": "ok", "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z"}

    upload_folder = os.path.abspath(flask_app.config.get("UPLOAD_FOLDER", "uploads"))
    @flask_app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(upload_folder, filename)

    @flask_app.errorhandler(500)
    def handle_500(e):
        return {"error": str(e) or "Internal server error"}, 500

    return flask_app
