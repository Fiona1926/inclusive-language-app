"""
SQLAlchemy models for language learning app.
"""
from app import db
from datetime import datetime
import uuid


def generate_id():
    return str(uuid.uuid4())[:25]


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    native_language = db.Column(db.String(10), default="en")
    learning_language = db.Column(db.String(10), default="en")
    tts_stt_mode_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    progress = db.relationship("UserLevelProgress", back_populates="user", cascade="all, delete-orphan")
    reading_attempts = db.relationship("ReadingAttempt", back_populates="user", cascade="all, delete-orphan")
    listening_attempts = db.relationship("ListeningAttempt", back_populates="user", cascade="all, delete-orphan")
    writing_submissions = db.relationship("WritingSubmission", back_populates="user", cascade="all, delete-orphan")
    speaking_attempts = db.relationship("SpeakingAttempt", back_populates="user", cascade="all, delete-orphan")
    feedback = db.relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

    levels = db.relationship("Level", back_populates="category", cascade="all, delete-orphan")
    progress = db.relationship("UserLevelProgress", back_populates="category", cascade="all, delete-orphan")


class Level(db.Model):
    __tablename__ = "levels"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    category_id = db.Column(db.String(36), db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    category = db.relationship("Category", back_populates="levels")
    progress = db.relationship("UserLevelProgress", back_populates="level", cascade="all, delete-orphan")
    reading_texts = db.relationship("ReadingText", back_populates="level", cascade="all, delete-orphan")
    listening_audios = db.relationship("ListeningAudio", back_populates="level", cascade="all, delete-orphan")
    writing_topics = db.relationship("WritingTopic", back_populates="level", cascade="all, delete-orphan")
    speaking_exercises = db.relationship("SpeakingExercise", back_populates="level", cascade="all, delete-orphan")


class UserLevelProgress(db.Model):
    __tablename__ = "user_level_progress"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    level_id = db.Column(db.String(36), db.ForeignKey("levels.id", ondelete="CASCADE"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="progress")
    category = db.relationship("Category", back_populates="progress")
    level = db.relationship("Level", back_populates="progress")

    __table_args__ = (db.UniqueConstraint("user_id", "category_id", "level_id", name="uq_user_category_level"),)


# --- Reading ---
class ReadingText(db.Model):
    __tablename__ = "reading_texts"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    level_id = db.Column(db.String(36), db.ForeignKey("levels.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)

    level = db.relationship("Level", back_populates="reading_texts")
    questions = db.relationship("ReadingQuestion", back_populates="reading_text", cascade="all, delete-orphan")
    attempts = db.relationship("ReadingAttempt", back_populates="reading_text", cascade="all, delete-orphan")


class ReadingQuestion(db.Model):
    __tablename__ = "reading_questions"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    reading_text_id = db.Column(db.String(36), db.ForeignKey("reading_texts.id", ondelete="CASCADE"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text)  # JSON
    correct_answer = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, default=0)

    reading_text = db.relationship("ReadingText", back_populates="questions")


class ReadingAttempt(db.Model):
    __tablename__ = "reading_attempts"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reading_text_id = db.Column(db.String(36), db.ForeignKey("reading_texts.id", ondelete="CASCADE"), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON
    score = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reading_attempts")
    reading_text = db.relationship("ReadingText", back_populates="attempts")
    feedback = db.relationship("Feedback", back_populates="reading_attempt", uselist=False, cascade="all, delete-orphan")


# --- Listening ---
class ListeningAudio(db.Model):
    __tablename__ = "listening_audios"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    level_id = db.Column(db.String(36), db.ForeignKey("levels.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    audio_url = db.Column(db.String(500), nullable=False)
    transcript = db.Column(db.Text)
    duration_seconds = db.Column(db.Integer)
    order = db.Column(db.Integer, default=0)

    level = db.relationship("Level", back_populates="listening_audios")
    attempts = db.relationship("ListeningAttempt", back_populates="audio", cascade="all, delete-orphan")


class ListeningAttempt(db.Model):
    __tablename__ = "listening_attempts"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listening_audio_id = db.Column(db.String(36), db.ForeignKey("listening_audios.id", ondelete="CASCADE"), nullable=False)
    user_translation = db.Column(db.Text, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="listening_attempts")
    audio = db.relationship("ListeningAudio", back_populates="attempts")
    feedback = db.relationship("Feedback", back_populates="listening_attempt", uselist=False, cascade="all, delete-orphan")


# --- Writing ---
class WritingTopic(db.Model):
    __tablename__ = "writing_topics"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    level_id = db.Column(db.String(36), db.ForeignKey("levels.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)

    level = db.relationship("Level", back_populates="writing_topics")
    submissions = db.relationship("WritingSubmission", back_populates="topic", cascade="all, delete-orphan")


class WritingSubmission(db.Model):
    __tablename__ = "writing_submissions"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    writing_topic_id = db.Column(db.String(36), db.ForeignKey("writing_topics.id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="writing_submissions")
    topic = db.relationship("WritingTopic", back_populates="submissions")
    feedback = db.relationship("Feedback", back_populates="writing_submission", uselist=False, cascade="all, delete-orphan")


# --- Speaking ---
class SpeakingExercise(db.Model):
    __tablename__ = "speaking_exercises"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    level_id = db.Column(db.String(36), db.ForeignKey("levels.id", ondelete="CASCADE"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # read_aloud | conversation
    title = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    sample_audio_url = db.Column(db.String(500))
    order = db.Column(db.Integer, default=0)

    level = db.relationship("Level", back_populates="speaking_exercises")
    attempts = db.relationship("SpeakingAttempt", back_populates="exercise", cascade="all, delete-orphan")


class SpeakingAttempt(db.Model):
    __tablename__ = "speaking_attempts"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = db.Column(db.String(36), db.ForeignKey("speaking_exercises.id", ondelete="CASCADE"), nullable=False)
    audio_url = db.Column(db.String(500))
    transcript = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="speaking_attempts")
    exercise = db.relationship("SpeakingExercise", back_populates="attempts")
    feedback = db.relationship("Feedback", back_populates="speaking_attempt", uselist=False, cascade="all, delete-orphan")


# --- Feedback ---
class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    scores = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = db.relationship("User", back_populates="feedback")

    reading_attempt_id = db.Column(db.String(36), db.ForeignKey("reading_attempts.id", ondelete="CASCADE"), unique=True)
    reading_attempt = db.relationship("ReadingAttempt", back_populates="feedback")
    listening_attempt_id = db.Column(db.String(36), db.ForeignKey("listening_attempts.id", ondelete="CASCADE"), unique=True)
    listening_attempt = db.relationship("ListeningAttempt", back_populates="feedback")
    writing_submission_id = db.Column(db.String(36), db.ForeignKey("writing_submissions.id", ondelete="CASCADE"), unique=True)
    writing_submission = db.relationship("WritingSubmission", back_populates="feedback")
    speaking_attempt_id = db.Column(db.String(36), db.ForeignKey("speaking_attempts.id", ondelete="CASCADE"), unique=True)
    speaking_attempt = db.relationship("SpeakingAttempt", back_populates="feedback")


# --- Reels ---
class ReelBatch(db.Model):
    """A group of 5 short reels; after these, one question (crafted from the videos' audio)."""
    __tablename__ = "reel_batches"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    title = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reels = db.relationship("Reel", back_populates="batch", cascade="all, delete-orphan", order_by="Reel.order_in_batch")
    question = db.relationship("ReelBatchQuestion", back_populates="batch", uselist=False, cascade="all, delete-orphan")
    attempts = db.relationship("ReelBatchAttempt", back_populates="batch", cascade="all, delete-orphan")


class ReelBatchQuestion(db.Model):
    """One question per batch, crafted from the audio of the 5 videos."""
    __tablename__ = "reel_batch_questions"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    reel_batch_id = db.Column(db.String(36), db.ForeignKey("reel_batches.id", ondelete="CASCADE"), nullable=False, unique=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON array of choices
    correct_answer = db.Column(db.String(500), nullable=False)

    batch = db.relationship("ReelBatch", back_populates="question")


class ReelBatchAttempt(db.Model):
    """Learner's answer to a batch question."""
    __tablename__ = "reel_batch_attempts"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reel_batch_id = db.Column(db.String(36), db.ForeignKey("reel_batches.id", ondelete="CASCADE"), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="reel_batch_attempts")
    batch = db.relationship("ReelBatch", back_populates="attempts")


class Reel(db.Model):
    __tablename__ = "reels"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    duration_seconds = db.Column(db.Integer)
    language = db.Column(db.String(10), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Batch: creator uploads 5 reels per batch; question follows (crafted from audio)
    batch_id = db.Column(db.String(36), db.ForeignKey("reel_batches.id", ondelete="SET NULL"))
    order_in_batch = db.Column(db.Integer)  # 1-5 within batch

    batch = db.relationship("ReelBatch", back_populates="reels")
    dubbings = db.relationship("ReelDubbing", back_populates="reel", cascade="all, delete-orphan")


class ReelDubbing(db.Model):
    __tablename__ = "reel_dubbings"
    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    reel_id = db.Column(db.String(36), db.ForeignKey("reels.id", ondelete="CASCADE"), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    audio_url = db.Column(db.String(500), nullable=False)
    transcript = db.Column(db.Text)

    reel = db.relationship("Reel", back_populates="dubbings")

    __table_args__ = (db.UniqueConstraint("reel_id", "language", name="uq_reel_language"),)
