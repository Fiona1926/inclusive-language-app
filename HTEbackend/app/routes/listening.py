"""
Listening: audio → translate. Submit translation, get feedback, track level completion.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import ListeningAudio, ListeningAttempt, UserLevelProgress
from app.services.feedback import create_feedback, generate_listening_feedback

listening_bp = Blueprint("listening", __name__)


@listening_bp.route("/levels/<level_id>/audios", methods=["GET"])
@jwt_required()
def level_audios(level_id):
    audios = ListeningAudio.query.filter_by(level_id=level_id).order_by(ListeningAudio.order).all()
    return jsonify([
        {"id": a.id, "title": a.title, "audioUrl": a.audio_url, "durationSeconds": a.duration_seconds, "order": a.order}
        for a in audios
    ])


@listening_bp.route("/audios/<audio_id>/submit", methods=["POST"])
@jwt_required()
def submit_listening(audio_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    user_translation = (data.get("userTranslation") or "").strip()
    if not user_translation:
        return jsonify({"error": "userTranslation required"}), 400

    audio = ListeningAudio.query.get(audio_id)
    if not audio:
        return jsonify({"error": "Listening audio not found"}), 404

    attempt = ListeningAttempt(
        user_id=user_id,
        listening_audio_id=audio_id,
        user_translation=user_translation,
    )
    db.session.add(attempt)
    db.session.commit()

    feedback_content = generate_listening_feedback(user_translation, audio.transcript)
    create_feedback(
        user_id=user_id,
        type="listening",
        content=feedback_content,
        listening_attempt_id=attempt.id,
    )

    level_id = audio.level_id
    category_id = audio.level.category_id
    all_audio_ids = [a.id for a in ListeningAudio.query.filter_by(level_id=level_id).all()]
    count = ListeningAttempt.query.filter(
        ListeningAttempt.user_id == user_id,
        ListeningAttempt.listening_audio_id.in_(all_audio_ids),
    ).count()
    if count >= len(all_audio_ids):
        existing = UserLevelProgress.query.filter_by(
            user_id=user_id, category_id=category_id, level_id=level_id
        ).first()
        if existing:
            existing.completed = True
            existing.completed_at = datetime.utcnow()
        else:
            db.session.add(UserLevelProgress(
                user_id=user_id, category_id=category_id, level_id=level_id,
                completed=True, completed_at=datetime.utcnow(),
            ))
        db.session.commit()

    return jsonify({"attemptId": attempt.id, "feedback": feedback_content}), 201
