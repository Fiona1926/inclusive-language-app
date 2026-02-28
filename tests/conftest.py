import os
import pytest

from app import create_app, db as _db
from app.models import (
    Category,
    Level,
    ReadingText,
    ReadingQuestion,
)


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.db"

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret"
        JWT_SECRET_KEY = "test-jwt-secret"
        JWT_ACCESS_TOKEN_EXPIRES = False
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        OPENAI_API_KEY = ""
        UPLOAD_FOLDER = str(tmp_path / "uploads")

    app = create_app(TestConfig)

    yield app

    with app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seed_categories(app):
    with app.app_context():
        # 4 categories + one level each
        cats = []
        for slug, name, order in [
            ("reading", "Reading", 1),
            ("writing", "Writing", 2),
            ("listening", "Listening", 3),
            ("speaking", "Speaking", 4),
        ]:
            c = Category.query.filter_by(slug=slug).first()
            if not c:
                c = Category(slug=slug, name=name, description=None, order=order)
                _db.session.add(c)
            cats.append(c)
        _db.session.commit()

        for c in cats:
            if not Level.query.filter_by(category_id=c.id, order=1).first():
                _db.session.add(
                    Level(category_id=c.id, order=1, name="Level 1", description=None)
                )
        _db.session.commit()

        return {c.slug: c for c in cats}


@pytest.fixture()
def seed_reading_content(app, seed_categories):
    with app.app_context():
        reading_cat = seed_categories["reading"]
        level = Level.query.filter_by(category_id=reading_cat.id, order=1).first()

        text = ReadingText.query.filter_by(level_id=level.id).first()
        if not text:
            text = ReadingText(
                level_id=level.id,
                title="Welcome",
                body="This is a sample reading text.",
                order=0,
            )
            _db.session.add(text)
            _db.session.commit()

        q = ReadingQuestion.query.filter_by(reading_text_id=text.id).first()
        if not q:
            q = ReadingQuestion(
                reading_text_id=text.id,
                question="What is this text about?",
                options='["A sample","Nothing","Welcome"]',
                correct_answer="A sample",
                order=0,
            )
            _db.session.add(q)
            _db.session.commit()

        return {"category": reading_cat, "level": level, "text": text, "question": q}

