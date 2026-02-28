"""
Inclusive mode: Text-to-Speech and Speech-to-Text.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.tts_stt import text_to_speech, speech_to_text

tts_stt_bp = Blueprint("tts_stt", __name__)


@tts_stt_bp.route("/tts", methods=["POST"])
@jwt_required()
def tts():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    result = text_to_speech(
        text=text,
        language=data.get("language"),
        voice=data.get("voice"),
    )
    if not result.get("success"):
        return jsonify({"error": result.get("error", "TTS failed")}), 503
    return jsonify({"audioUrl": result.get("audioUrl")})


@tts_stt_bp.route("/stt", methods=["POST"])
@jwt_required()
def stt():
    data = request.get_json() or {}
    audio = (data.get("audioUrlOrBase64") or "").strip()
    if not audio:
        return jsonify({"error": "audioUrlOrBase64 required"}), 400
    result = speech_to_text(
        audio_url_or_base64=audio,
        language=data.get("language"),
    )
    if not result.get("success"):
        return jsonify({"error": result.get("error", "STT failed")}), 503
    return jsonify({"text": result.get("text")})
