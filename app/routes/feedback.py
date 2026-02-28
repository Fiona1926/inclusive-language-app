"""
Fetch feedback by type or by attempt/submission id.
"""
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Feedback

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("", methods=["GET"])
@feedback_bp.route("/", methods=["GET"])
@jwt_required()
def list_feedback():
    user_id = get_jwt_identity()
    type_filter = request.args.get("type")
    if type_filter and type_filter in ("reading", "listening", "writing", "speaking"):
        items = Feedback.query.filter_by(user_id=user_id, type=type_filter).order_by(Feedback.created_at.desc()).limit(100).all()
    else:
        items = Feedback.query.filter_by(user_id=user_id).order_by(Feedback.created_at.desc()).limit(100).all()
    return jsonify([
        {
            "id": f.id,
            "type": f.type,
            "content": f.content,
            "scores": json.loads(f.scores) if f.scores else None,
            "createdAt": f.created_at.isoformat(),
        }
        for f in items
    ])


@feedback_bp.route("/reading/<attempt_id>", methods=["GET"])
@jwt_required()
def get_reading_feedback(attempt_id):
    user_id = get_jwt_identity()
    f = Feedback.query.filter_by(
        user_id=user_id, type="reading", reading_attempt_id=attempt_id
    ).first()
    if not f:
        return jsonify({"error": "Feedback not found"}), 404
    return jsonify({
        "id": f.id,
        "type": f.type,
        "content": f.content,
        "scores": json.loads(f.scores) if f.scores else None,
        "createdAt": f.created_at.isoformat(),
    })


@feedback_bp.route("/listening/<attempt_id>", methods=["GET"])
@jwt_required()
def get_listening_feedback(attempt_id):
    user_id = get_jwt_identity()
    f = Feedback.query.filter_by(
        user_id=user_id, type="listening", listening_attempt_id=attempt_id
    ).first()
    if not f:
        return jsonify({"error": "Feedback not found"}), 404
    return jsonify({
        "id": f.id,
        "type": f.type,
        "content": f.content,
        "scores": json.loads(f.scores) if f.scores else None,
        "createdAt": f.created_at.isoformat(),
    })


@feedback_bp.route("/writing/<submission_id>", methods=["GET"])
@jwt_required()
def get_writing_feedback(submission_id):
    user_id = get_jwt_identity()
    f = Feedback.query.filter_by(
        user_id=user_id, type="writing", writing_submission_id=submission_id
    ).first()
    if not f:
        return jsonify({"error": "Feedback not found"}), 404
    return jsonify({
        "id": f.id,
        "type": f.type,
        "content": f.content,
        "scores": json.loads(f.scores) if f.scores else None,
        "createdAt": f.created_at.isoformat(),
    })


@feedback_bp.route("/speaking/<attempt_id>", methods=["GET"])
@jwt_required()
def get_speaking_feedback(attempt_id):
    user_id = get_jwt_identity()
    f = Feedback.query.filter_by(
        user_id=user_id, type="speaking", speaking_attempt_id=attempt_id
    ).first()
    if not f:
        return jsonify({"error": "Feedback not found"}), 404
    return jsonify({
        "id": f.id,
        "type": f.type,
        "content": f.content,
        "scores": json.loads(f.scores) if f.scores else None,
        "createdAt": f.created_at.isoformat(),
    })
