"""
Text-to-Speech and Speech-to-Text (inclusive mode).
- TTS: MiniMax when MINIMAX_API_KEY is set.
- STT: Local Whisper (openai-whisper) for voice answers in lessons; no API key required.
"""
import base64
import logging
import os
import re
import tempfile
import threading
import uuid
import requests
from config import Config

logger = logging.getLogger(__name__)

# Lazy-loaded local Whisper model (shared across requests)
_whisper_model = None
_whisper_lock = threading.Lock()


def _get_whisper_model():
    """Load and cache the local Whisper model. Thread-safe."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    with _whisper_lock:
        if _whisper_model is not None:
            return _whisper_model
        import whisper
        model_name = getattr(Config, "WHISPER_MODEL", None) or os.environ.get("WHISPER_MODEL") or "base"
        logger.info("Loading local Whisper model: %s", model_name)
        _whisper_model = whisper.load_model(model_name)
        return _whisper_model


MINIMAX_T2A_URL = "https://api.minimax.io/v1/t2a_v2"


def text_to_speech(text: str, language: str | None = None, voice: str | None = None) -> dict:
    if not Config.MINIMAX_API_KEY:
        return {"success": False, "error": "TTS not configured. Set MINIMAX_API_KEY."}
    payload = {
        "model": "speech-2.8-hd",
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice or "English_expressive_narrator",
            "speed": 1,
            "vol": 1,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
        "output_format": "hex",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + Config.MINIMAX_API_KEY,
    }
    try:
        resp = requests.post(MINIMAX_T2A_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
    except ValueError as e:
        return {"success": False, "error": "Invalid MiniMax response: " + str(e)}

    audio_hex = (data.get("data") or {}).get("audio")
    if not audio_hex:
        return {"success": False, "error": data.get("base_resp", {}).get("status_msg") or "No audio in response."}

    try:
        audio_bytes = bytes.fromhex(audio_hex)
    except (TypeError, ValueError) as e:
        return {"success": False, "error": "Invalid audio hex: " + str(e)}

    upload_dir = os.path.abspath(Config.UPLOAD_FOLDER)
    tts_dir = os.path.join(upload_dir, "tts")
    os.makedirs(tts_dir, exist_ok=True)
    filename = uuid.uuid4().hex + ".mp3"
    filepath = os.path.join(tts_dir, filename)
    try:
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
    except OSError as e:
        return {"success": False, "error": "Failed to save audio: " + str(e)}

    audio_url = "/uploads/tts/" + filename
    return {"success": True, "audioUrl": audio_url}


def _infer_audio_suffix_from_url(url: str, content_type: str | None) -> str:
    """Infer file suffix for Whisper from URL path or Content-Type."""
    if content_type:
        if "webm" in content_type:
            return ".webm"
        if "mp3" in content_type or "mpeg" in content_type:
            return ".mp3"
        if "wav" in content_type:
            return ".wav"
        if "ogg" in content_type:
            return ".ogg"
        if "m4a" in content_type or "mp4" in content_type:
            return ".m4a"
    path = url.split("?")[0].lower()
    if path.endswith(".mp3"):
        return ".mp3"
    if path.endswith(".webm"):
        return ".webm"
    if path.endswith(".wav"):
        return ".wav"
    if path.endswith(".m4a") or path.endswith(".mp4"):
        return ".m4a"
    return ".webm"


def speech_to_text(audio_url_or_base64: str, language: str | None = None) -> dict:
    """Transcribe audio to text using local Whisper (openai-whisper).
    Accepts either a remote audio URL (http/https) or base64 audio (optionally with data URL prefix).
    Default language is Indonesian (id). No API key required.
    """
    raw = (audio_url_or_base64 or "").strip()
    if not raw:
        logger.warning("STT: no audio data provided")
        return {"success": False, "error": "No audio data provided."}

    is_url = raw.startswith("http://") or raw.startswith("https://")
    logger.info(
        "STT input: len=%s is_url=%s preview=%s",
        len(raw),
        is_url,
        raw[:80] + "..." if len(raw) > 80 and not raw.startswith("data:") else "[base64/data URL]",
    )

    audio_bytes = None
    suffix = ".webm"

    if is_url:
        try:
            resp = requests.get(raw, timeout=30)
            resp.raise_for_status()
            audio_bytes = resp.content
            content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip()
            suffix = _infer_audio_suffix_from_url(raw, content_type)
            logger.info("STT URL fetched: bytes=%s content_type=%s suffix=%s", len(audio_bytes), content_type, suffix)
        except requests.RequestException as e:
            logger.exception("STT URL fetch failed: %s", raw)
            return {"success": False, "error": "Failed to fetch audio URL: " + str(e)}
    else:
        # Strip data URL prefix if present (e.g. data:audio/webm;base64,)
        b64 = re.sub(r"^data:audio/[^;]+;base64,", "", raw)
        logger.info("STT base64: payload_len=%s after_strip=%s", len(raw), len(b64))
        # Allow decoding with optional padding (some clients omit trailing =)
        try:
            audio_bytes = base64.b64decode(b64, validate=False)
        except Exception as e:
            logger.exception("STT base64 decode failed")
            return {"success": False, "error": "Invalid base64: " + str(e)}
        if raw.strip().lower().startswith("data:audio/"):
            match = re.search(r"^data:audio/([^;]+);", raw.strip().lower())
            if match:
                ext = match.group(1).split("/")[-1].strip()
                if ext in ("webm", "mp3", "wav", "ogg", "m4a", "mp4"):
                    suffix = "." + ext

    if not audio_bytes:
        logger.warning("STT: empty audio after decode/fetch")
        return {"success": False, "error": "Empty audio data."}
    logger.info("STT audio_bytes=%s suffix=%s sending to local Whisper", len(audio_bytes), suffix)

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            model = _get_whisper_model()
            lang = (language or "id").strip() or None
            result = model.transcribe(tmp_path, language=lang, fp16=False)
            text = (result.get("text") or "").strip()
            logger.info("STT success: text_len=%s", len(text))
            return {"success": True, "text": text}
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except Exception as e:
        logger.exception("STT Whisper failed")
        return {"success": False, "error": str(e)}
