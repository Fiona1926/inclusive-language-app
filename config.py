"""
Central config from environment.
Used for server, database, JWT, and optional TTS/STT API keys.
"""
import os
from dotenv import load_dotenv

load_dotenv() # load environment variables from .env file


class Config:
    # secret key for signing JWT tokens
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"
    # database URI for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # secret key to stay logged in
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET") or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 7 * 24 * 3600  # 7 days
    
    # OpenAI API key (e.g. for AI feedback); STT uses local Whisper, not OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or ""
    # MiniMax API key for TTS (text-to-audio)
    MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY") or ""
    # Local Whisper model for STT: tiny, base, small, medium, large-v2, large-v3
    WHISPER_MODEL = os.environ.get("WHISPER_MODEL") or "base"
    # folder for uploaded files
    UPLOAD_FOLDER = os.environ.get("UPLOAD_DIR") or "uploads"
