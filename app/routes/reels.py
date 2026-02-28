"""
Reels: short videos with dubbing. Creators upload videos; every 5 reels form a batch
with one question crafted from the videos' audio.
"""
import json
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app import db
from app.models import Reel, ReelDubbing, ReelBatch, ReelBatchQuestion, ReelBatchAttempt

reels_bp = Blueprint("reels", __name__)

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "avi"}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_VIDEO_EXTENSIONS


def _reel_to_json(r):
    return {
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "videoUrl": r.video_url,
        "thumbnailUrl": r.thumbnail_url,
        "durationSeconds": r.duration_seconds,
        "language": r.language,
        "order": r.order,
        "batchId": r.batch_id,
        "orderInBatch": r.order_in_batch,
        "dubbings": [{"id": d.id, "language": d.language, "audioUrl": d.audio_url} for d in r.dubbings],
    }


# ---------- Creator: batches and upload ----------
@reels_bp.route("/batches", methods=["POST"])
@jwt_required()
def create_batch():
    """Create a new batch (group of 5 reels). Creator then uploads 5 videos to this batch."""
    data = request.get_json() or {}
    title = (data.get("title") or "").strip() or None
    order = data.get("order", 0)
    batch = ReelBatch(title=title, order=order)
    db.session.add(batch)
    db.session.commit()
    return jsonify({"id": batch.id, "title": batch.title, "order": batch.order}), 201


@reels_bp.route("/batches", methods=["GET"])
def list_batches():
    """List all batches with their reels (ordered 1–5) and question if set."""
    batches = ReelBatch.query.order_by(ReelBatch.order).all()
    out = []
    for b in batches:
        reels = Reel.query.filter_by(batch_id=b.id).order_by(Reel.order_in_batch).all()
        q = ReelBatchQuestion.query.filter_by(reel_batch_id=b.id).first()
        out.append({
            "id": b.id,
            "title": b.title,
            "order": b.order,
            "createdAt": b.created_at.isoformat() if b.created_at else None,
            "reels": [_reel_to_json(r) for r in reels],
            "question": {
                "id": q.id,
                "question": q.question,
                "options": json.loads(q.options) if q.options else [],
                "correctAnswer": q.correct_answer,
            } if q else None,
        })
    return jsonify(out)


@reels_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_reel():
    """Creator uploads a video. Optional: attach to a batch with order_in_batch (1–5)."""
    if "video" not in request.files and "file" not in request.files:
        return jsonify({"error": "No video file (use form key 'video' or 'file')"}), 400
    file = request.files.get("video") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No video file selected"}), 400
    if not _allowed_file(file.filename):
        return jsonify({"error": f"Allowed formats: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"}), 400

    title = (request.form.get("title") or "Untitled").strip()
    description = (request.form.get("description") or "").strip() or None
    language = (request.form.get("language") or "en").strip()
    batch_id = request.form.get("batchId") or request.form.get("batch_id")
    order_in_batch = request.form.get("orderInBatch") or request.form.get("order_in_batch")
    if order_in_batch is not None:
        try:
            order_in_batch = int(order_in_batch)
        except ValueError:
            order_in_batch = None

    upload_dir = os.path.join(current_app.config.get("UPLOAD_FOLDER", "uploads"), "reels")
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1].lower()
    safe = secure_filename(file.filename) or "video"
    base = f"{safe.rsplit('.', 1)[0]}_{os.urandom(4).hex()}"
    filename = f"{base}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    video_url = f"/uploads/reels/{filename}"

    reel = Reel(
        title=title,
        description=description,
        video_url=video_url,
        language=language,
        batch_id=batch_id or None,
        order_in_batch=order_in_batch,
    )
    db.session.add(reel)
    db.session.commit()
    return jsonify(_reel_to_json(reel)), 201


@reels_bp.route("/batches/<batch_id>/question", methods=["POST"])
@jwt_required()
def set_batch_question(batch_id):
    """Set the question for a batch (crafted from the audio of the 5 videos). One question per batch."""
    batch = ReelBatch.query.get(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    options = data.get("options")
    correct_answer = (data.get("correctAnswer") or data.get("correct_answer") or "").strip()
    if not question:
        return jsonify({"error": "question required"}), 400
    if not isinstance(options, list):
        return jsonify({"error": "options must be an array"}), 400
    if not correct_answer:
        return jsonify({"error": "correctAnswer required"}), 400

    existing = ReelBatchQuestion.query.filter_by(reel_batch_id=batch_id).first()
    if existing:
        existing.question = question
        existing.options = json.dumps(options)
        existing.correct_answer = correct_answer
        db.session.commit()
        return jsonify({"id": existing.id, "question": question, "options": options, "correctAnswer": correct_answer})
    q = ReelBatchQuestion(reel_batch_id=batch_id, question=question, options=json.dumps(options), correct_answer=correct_answer)
    db.session.add(q)
    db.session.commit()
    return jsonify({"id": q.id, "question": question, "options": options, "correctAnswer": correct_answer}), 201


# ---------- Learner: watch reels and answer question ----------
@reels_bp.route("", methods=["GET"])
@reels_bp.route("/", methods=["GET"])
def list_reels():
    reels = Reel.query.order_by(Reel.order, Reel.order_in_batch).all()
    return jsonify([_reel_to_json(r) for r in reels])


@reels_bp.route("/<reel_id>", methods=["GET"])
def get_reel(reel_id):
    reel = Reel.query.get(reel_id)
    if not reel:
        return jsonify({"error": "Reel not found"}), 404
    out = _reel_to_json(reel)
    out["dubbings"] = [{"id": d.id, "language": d.language, "audioUrl": d.audio_url, "transcript": d.transcript} for d in reel.dubbings]
    return jsonify(out)


@reels_bp.route("/batches/<batch_id>", methods=["GET"])
def get_batch(batch_id):
    """Get one batch with its 5 reels and the question (for learners)."""
    batch = ReelBatch.query.get(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404
    reels = Reel.query.filter_by(batch_id=batch_id).order_by(Reel.order_in_batch).all()
    q = ReelBatchQuestion.query.filter_by(reel_batch_id=batch_id).first()
    return jsonify({
        "id": batch.id,
        "title": batch.title,
        "order": batch.order,
        "reels": [_reel_to_json(r) for r in reels],
        "question": {
            "id": q.id,
            "question": q.question,
            "options": json.loads(q.options) if q.options else [],
        } if q else None,
    })


@reels_bp.route("/batches/<batch_id>/submit", methods=["POST"])
@jwt_required()
def submit_batch_answer(batch_id):
    """Learner submits their answer to the batch question (after watching the 5 videos)."""
    user_id = get_jwt_identity()
    batch = ReelBatch.query.get(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404
    q = ReelBatchQuestion.query.filter_by(reel_batch_id=batch_id).first()
    if not q:
        return jsonify({"error": "No question set for this batch"}), 404
    data = request.get_json() or {}
    answer = (data.get("answer") or "").strip()
    if not answer:
        return jsonify({"error": "answer required"}), 400

    correct = answer == q.correct_answer
    attempt = ReelBatchAttempt(user_id=user_id, reel_batch_id=batch_id, answer=answer, correct=correct)
    db.session.add(attempt)
    db.session.commit()
    return jsonify({
        "attemptId": attempt.id,
        "correct": correct,
        "correctAnswer": q.correct_answer,
    }), 201


@reels_bp.route("/<reel_id>/dubbing", methods=["GET"])
def get_dubbing(reel_id):
    language = request.args.get("language", "en")
    dubbing = ReelDubbing.query.filter_by(reel_id=reel_id, language=language).first()
    if not dubbing:
        return jsonify({"error": "Dubbing not found for this language"}), 404
    return jsonify({
        "id": dubbing.id,
        "reelId": dubbing.reel_id,
        "language": dubbing.language,
        "audioUrl": dubbing.audio_url,
        "transcript": dubbing.transcript,
    })
