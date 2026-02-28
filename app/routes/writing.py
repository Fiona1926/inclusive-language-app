"""
Writing: topic → essay. Submit content, get feedback, track level completion.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import WritingTopic, WritingSubmission, UserLevelProgress
from app.services.feedback import create_feedback, generate_writing_feedback

writing_bp = Blueprint("writing", __name__)


@writing_bp.route("/levels/<level_id>/topics", methods=["GET"])
@jwt_required()
def level_topics(level_id):
    topics = WritingTopic.query.filter_by(level_id=level_id).order_by(WritingTopic.order).all()
    return jsonify([
        {"id": t.id, "title": t.title, "prompt": t.prompt, "order": t.order}
        for t in topics
    ])


@writing_bp.route("/topics/<topic_id>/submit", methods=["POST"])
@jwt_required()
def submit_writing(topic_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content required"}), 400

    topic = WritingTopic.query.get(topic_id)
    if not topic:
        return jsonify({"error": "Writing topic not found"}), 404

    submission = WritingSubmission(
        user_id=user_id,
        writing_topic_id=topic_id,
        content=content,
    )
    db.session.add(submission)
    db.session.commit()

    feedback_content = generate_writing_feedback(topic.prompt, content)
    create_feedback(
        user_id=user_id,
        type="writing",
        content=feedback_content,
        writing_submission_id=submission.id,
    )

    level_id = topic.level_id
    category_id = topic.level.category_id
    all_topic_ids = [t.id for t in WritingTopic.query.filter_by(level_id=level_id).all()]
    count = WritingSubmission.query.filter(
        WritingSubmission.user_id == user_id,
        WritingSubmission.writing_topic_id.in_(all_topic_ids),
    ).count()
    if count >= len(all_topic_ids):
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

    return jsonify({"submissionId": submission.id, "feedback": feedback_content}), 201
