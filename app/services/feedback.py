"""
Feedback generation for each category.
"""
# When run as script, ensure project root is on path so "app" can be imported.
if __name__ == "__main__":
    import os
    import sys
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _root not in sys.path:
        sys.path.insert(0, _root)

import json
from app import db
from app.models import Feedback
from config import Config


def create_feedback(
    user_id: str,
    type: str,
    content: str,
    scores: dict | None = None,
    reading_attempt_id: str | None = None,
    listening_attempt_id: str | None = None,
    writing_submission_id: str | None = None,
    speaking_attempt_id: str | None = None,
) -> Feedback:
    f = Feedback(
        user_id=user_id,
        type=type,
        content=content,
        scores=json.dumps(scores) if scores else None,
        reading_attempt_id=reading_attempt_id,
        listening_attempt_id=listening_attempt_id,
        writing_submission_id=writing_submission_id,
        speaking_attempt_id=speaking_attempt_id,
    )
    db.session.add(f)
    db.session.commit()
    return f


def generate_reading_feedback(
    correct_count: int,
    total_count: int,
    wrong_questions: list | None = None,
) -> str:
    pct = round((correct_count / total_count) * 100) if total_count else 0
    text = f"You got {correct_count}/{total_count} ({pct}%) correct."
    if wrong_questions:
        text += "\nReview: " + "; ".join(
            f'("{q["question"]}" → {q["correct"]})' for q in wrong_questions
        )
    return text



def generate_listening_feedback(user_translation: str, reference_transcript: str | None = None) -> str:
    if not reference_transcript:
        return "Translation submitted. Enable reference transcript for detailed feedback."
    return "Compare your translation with the transcript and improve where needed."


def generate_writing_feedback(topic: str, essay: str) -> str:
    if not Config.OPENAI_API_KEY:
        return "Essay submitted. Enable OPENAI_API_KEY for AI feedback on grammar and clarity."
    return "Essay submitted. AI feedback can be added here via OpenAI."


def generate_speaking_feedback(
    pronunciation: int | None = None,
    fluency: int | None = None,
    dictation: int | None = None,
) -> tuple[str, dict]:
    parts = []
    scores = {}
    if pronunciation is not None:
        parts.append(f"Pronunciation: {pronunciation}/10")
        scores["pronunciation"] = pronunciation
    if fluency is not None:
        parts.append(f"Fluency: {fluency}/10")
        scores["fluency"] = fluency
    if dictation is not None:
        parts.append(f"Dictation: {dictation}/10")
        scores["dictation"] = dictation
    content = ". ".join(parts) if parts else "Speaking attempt recorded. Enable assessment API for scores."
    return content, scores
