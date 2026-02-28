"""
Text-to-Speech and Speech-to-Text (inclusive mode).
Uses external APIs when configured; returns clear message when not.
"""
from config import Config


def text_to_speech(text: str, language: str | None = None, voice: str | None = None) -> dict:
    if not Config.OPENAI_API_KEY:
        return {"success": False, "error": "TTS not configured. Set OPENAI_API_KEY."}
    return {
        "success": False,
        "error": "TTS integration: add OpenAI or Google TTS call here.",
    }


def speech_to_text(audio_url_or_base64: str, language: str | None = None) -> dict:
    if not Config.OPENAI_API_KEY:
        return {"success": False, "error": "STT not configured. Set OPENAI_API_KEY."}
    return {
        "success": False,
        "error": "STT integration: add Whisper or Google STT call here.",
    }
