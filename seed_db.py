"""
Seed categories, one level per category, sample reading text, and a sample reel.
Run: python seed_db.py  (after app has been run once so DB exists, or create_all first)
"""
from app import create_app, db
from app.models import Category, Level, ReadingText, ReadingQuestion, Reel

app = create_app()
with app.app_context():
    for slug, name, desc, order in [
        ("reading", "Reading", "Text-based quizzes", 1),
        ("writing", "Writing", "Essay writing by topic", 2),
        ("listening", "Listening", "Listen and translate", 3),
        ("speaking", "Speaking", "Read aloud and conversation", 4),
    ]:
        cat = Category.query.filter_by(slug=slug).first()
        if not cat:
            cat = Category(slug=slug, name=name, description=desc, order=order)
            db.session.add(cat)
            db.session.commit()

    for cat in Category.query.all():
        level = Level.query.filter_by(category_id=cat.id, order=1).first()
        if not level:
            level = Level(category_id=cat.id, order=1, name="Level 1", description=f"First level for {cat.name}")
            db.session.add(level)
            db.session.commit()

    reading_cat = Category.query.filter_by(slug="reading").first()
    if reading_cat:
        level1 = Level.query.filter_by(category_id=reading_cat.id, order=1).first()
        if level1 and not ReadingText.query.filter_by(level_id=level1.id).first():
            text = ReadingText(
                level_id=level1.id,
                title="Welcome",
                body="This is a sample reading text. Answer the question below.",
                order=0,
            )
            db.session.add(text)
            db.session.commit()
            q = ReadingQuestion(
                reading_text_id=text.id,
                question="What is this text about?",
                options='["A sample", "Nothing", "Welcome"]',
                correct_answer="A sample",
                order=0,
            )
            db.session.add(q)
            db.session.commit()

    if not Reel.query.filter_by(title="Sample Reel").first():
        reel = Reel(
            title="Sample Reel",
            description="Short video with dubbing",
            video_url="/uploads/sample.mp4",
            language="en",
            order=0,
        )
        db.session.add(reel)
        db.session.commit()

    print("Seed done.")
