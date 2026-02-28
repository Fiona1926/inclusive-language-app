"""
Speaking: read aloud / conversation. Submit audio/transcript and optional scores, get feedback.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import SpeakingExercise, SpeakingAttempt, UserLevelProgress
from app.services.feedback import create_feedback, generate_speaking_feedback

speaking_bp = Blueprint("speaking", __name__)


@speaking_bp.route("/levels/<level_id>/exercises", methods=["GET"])
@jwt_required()
def level_exercises(level_id):
    exercises = SpeakingExercise.query.filter_by(level_id=level_id).order_by(SpeakingExercise.order).all()
    return jsonify([
        {"id": e.id, "type": e.type, "title": e.title, "prompt": e.prompt, "sampleAudioUrl": e.sample_audio_url, "order": e.order}
        for e in exercises
    ])


@speaking_bp.route("/exercises/<exercise_id>/submit", methods=["POST"])
@jwt_required()
def submit_speaking(exercise_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    audio_url = data.get("audioUrl")
    transcript = data.get("transcript")
    pronunciation = data.get("pronunciation")
    fluency = data.get("fluency")
    dictation = data.get("dictation")

    exercise = SpeakingExercise.query.get(exercise_id)
    if not exercise:
        return jsonify({"error": "Speaking exercise not found"}), 404

    attempt = SpeakingAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        audio_url=audio_url,
        transcript=transcript,
    )
    db.session.add(attempt)
    db.session.commit()

    feedback_content, score_obj = generate_speaking_feedback(
        pronunciation=pronunciation, fluency=fluency, dictation=dictation
    )
    create_feedback(
        user_id=user_id,
        type="speaking",
        content=feedback_content,
        scores=score_obj if score_obj else None,
        speaking_attempt_id=attempt.id,
    )

    level_id = exercise.level_id
    category_id = exercise.level.category_id
    all_exercise_ids = [e.id for e in SpeakingExercise.query.filter_by(level_id=level_id).all()]
    count = SpeakingAttempt.query.filter(
        SpeakingAttempt.user_id == user_id,
        SpeakingAttempt.exercise_id.in_(all_exercise_ids),
    ).count()
    if count >= len(all_exercise_ids):
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

    return jsonify({
        "attemptId": attempt.id,
        "feedback": feedback_content,
        "scores": score_obj,
    }), 201
