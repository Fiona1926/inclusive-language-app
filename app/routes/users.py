"""
User profile and progress.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, UserLevelProgress

users_bp = Blueprint("users", __name__)


@users_bp.route("/profile", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        user.name = (data["name"] or "").strip() or None
    if "nativeLanguage" in data:
        user.native_language = (data["nativeLanguage"] or "en").strip()
    if "learningLanguage" in data:
        user.learning_language = (data["learningLanguage"] or "en").strip()
    if "ttsSttModeEnabled" in data:
        user.tts_stt_mode_enabled = bool(data["ttsSttModeEnabled"])
    db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "nativeLanguage": user.native_language,
        "learningLanguage": user.learning_language,
        "ttsSttModeEnabled": user.tts_stt_mode_enabled,
    })


@users_bp.route("/progress", methods=["GET"])
@jwt_required()
def progress():
    user_id = get_jwt_identity()
    rows = (
        UserLevelProgress.query.filter_by(user_id=user_id)
        .join(UserLevelProgress.level)
        .join(UserLevelProgress.category)
        .order_by(UserLevelProgress.category_id, UserLevelProgress.level_id)
        .all()
    )
    return jsonify([
        {
            "id": p.id,
            "categoryId": p.category_id,
            "levelId": p.level_id,
            "completed": p.completed,
            "completedAt": p.completed_at.isoformat() if p.completed_at else None,
            "level": {"id": p.level.id, "order": p.level.order, "name": p.level.name},
            "category": {"id": p.category.id, "slug": p.category.slug, "name": p.category.name},
        }
        for p in rows
    ])
