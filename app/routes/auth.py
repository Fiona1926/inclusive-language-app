"""
Auth: register, login, me.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
import bcrypt

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    name = (data.get("name") or "").strip() or None
    native_language = (data.get("nativeLanguage") or data.get("native_language") or "en").strip()
    learning_language = (data.get("learningLanguage") or data.get("learning_language") or "en").strip()

    if not email or "@" not in email:
        return jsonify({"error": "Valid email required"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(
        email=email,
        password_hash=password_hash,
        name=name,
        native_language=native_language,
        learning_language=learning_language,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id, additional_claims={"email": user.email})
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "nativeLanguage": user.native_language,
            "learningLanguage": user.learning_language,
            "ttsSttModeEnabled": user.tts_stt_mode_enabled,
        },
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=user.id, additional_claims={"email": user.email})
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "nativeLanguage": user.native_language,
            "learningLanguage": user.learning_language,
            "ttsSttModeEnabled": user.tts_stt_mode_enabled,
        },
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "nativeLanguage": user.native_language,
        "learningLanguage": user.learning_language,
        "ttsSttModeEnabled": user.tts_stt_mode_enabled,
    })
