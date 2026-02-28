"""
Reading: text-based quiz. Submit answers, get feedback, track level completion.
"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import ReadingText, ReadingQuestion, ReadingAttempt, UserLevelProgress
from app.services.feedback import create_feedback, generate_reading_feedback

reading_bp = Blueprint("reading", __name__)


@reading_bp.route("/levels/<level_id>/texts", methods=["GET"])
@jwt_required()
def level_texts(level_id):
    texts = ReadingText.query.filter_by(level_id=level_id).order_by(ReadingText.order).all()
    out = []
    for t in texts:
        questions = ReadingQuestion.query.filter_by(reading_text_id=t.id).order_by(ReadingQuestion.order).all()
        out.append({
            "id": t.id,
            "title": t.title,
            "body": t.body,
            "order": t.order,
            "questions": [
                {"id": q.id, "question": q.question, "options": json.loads(q.options) if q.options else None, "order": q.order}
                for q in questions
            ],
        })
    return jsonify(out)


@reading_bp.route("/texts/<text_id>", methods=["GET"])
@jwt_required()
def get_text(text_id):
    t = ReadingText.query.get(text_id)
    if not t:
        return jsonify({"error": "Reading text not found"}), 404
    questions = ReadingQuestion.query.filter_by(reading_text_id=t.id).order_by(ReadingQuestion.order).all()
    return jsonify({
        "id": t.id,
        "levelId": t.level_id,
        "title": t.title,
        "body": t.body,
        "order": t.order,
        "questions": [
            {"id": q.id, "question": q.question, "options": json.loads(q.options) if q.options else None, "order": q.order}
            for q in questions
        ],
    })


@reading_bp.route("/texts/<text_id>/submit", methods=["POST"])
@jwt_required()
def submit_reading(text_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    answers = data.get("answers")
    if not isinstance(answers, dict):
        return jsonify({"error": "answers must be an object"}), 400

    text = ReadingText.query.get(text_id)
    if not text:
        return jsonify({"error": "Reading text not found"}), 404

    questions_list = ReadingQuestion.query.filter_by(reading_text_id=text_id).all()
    total = len(questions_list)
    correct = 0
    wrong = []
    for q in questions_list:
        user_ans = answers.get(q.id)
        is_correct = user_ans is not None and user_ans == q.correct_answer
        if is_correct:
            correct += 1
        else:
            wrong.append({"question": q.question, "correct": q.correct_answer})
    score = round((correct / total) * 100) if total else 0

    attempt = ReadingAttempt(
        user_id=user_id,
        reading_text_id=text_id,
        answers=json.dumps(answers),
        score=score,
    )
    db.session.add(attempt)
    db.session.commit()

    feedback_content = generate_reading_feedback(correct, total, wrong)
    create_feedback(
        user_id=user_id,
        type="reading",
        content=feedback_content,
        reading_attempt_id=attempt.id,
    )

    level = text.level
    category_id = level.category_id
    level_id = level.id
    all_text_ids = [t.id for t in ReadingText.query.filter_by(level_id=level_id).all()]
    count_attempts = ReadingAttempt.query.filter(
        ReadingAttempt.user_id == user_id,
        ReadingAttempt.reading_text_id.in_(all_text_ids),
    ).count()
    if count_attempts >= len(all_text_ids):
        from app.models import UserLevelProgress
        existing = UserLevelProgress.query.filter_by(
            user_id=user_id, category_id=category_id, level_id=level_id
        ).first()
        if existing:
            existing.completed = True
            from datetime import datetime
            existing.completed_at = datetime.utcnow()
        else:
            db.session.add(UserLevelProgress(
                user_id=user_id, category_id=category_id, level_id=level_id,
                completed=True, completed_at=datetime.utcnow(),
            ))
        db.session.commit()

    return jsonify({
        "attemptId": attempt.id,
        "score": score,
        "correct": correct,
        "total": total,
        "feedback": feedback_content,
    }), 201
