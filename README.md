# LinguaScroll

**LinguaScroll** is an inclusive language learning web app with an integrated frontend and Flask backend. It offers four categories (Reading, Writing, Listening, Speaking), level-based progression, optional **text-to-speech / speech-to-text**, and **reels** with dubbing. The server serves both the API and the web UI (dashboard, lessons, profile).

---

## Quick start

```bash
cp .env.example .env
python -m venv venv
source venv/bin/activate   # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
python run.py
# In another terminal (with venv active):
python seed_db.py
```

Open **http://localhost:3000** in your browser to use the LinguaScroll dashboard. Set `OPENAI_API_KEY` in `.env` when you integrate TTS/STT.

---

## Testing (pytest)

```bash
source venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Tests use a temporary SQLite database and Flask’s `test_client` for the API.

---

## Project structure

### Root

| File / folder | Purpose |
|---------------|--------|
| **`requirements.txt`** | Dependencies: Flask, Flask-SQLAlchemy, Flask-CORS, Flask-JWT-Extended, bcrypt, python-dotenv, SQLAlchemy, pytest. |
| **`config.py`** | Loads env via `python-dotenv`. Defines `Config`: `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRES`, `OPENAI_API_KEY`, `UPLOAD_FOLDER`. |
| **`run.py`** | Entry point: creates app with `create_app()`, runs dev server (port from `PORT` or 3000). |
| **`seed_db.py`** | Seeds four categories, one level per category, one sample reading text with a quiz question, and one sample reel. Run once after DB exists. |
| **`templates/`** | **Frontend (LinguaScroll UI):** Jinja2 HTML — `index.html` (dashboard), `lessons.html`, `lesson.html`, `profile.html`. |
| **`static/`** | **Frontend assets:** `index.css`, `main.js`, `lesson.js`, `slides/`, and **`js/api.js`** — API client (`LinglongAPI`) for auth and data. |
| **`.env.example`** | Template for `PORT`, `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET`, `OPENAI_API_KEY`, `UPLOAD_DIR`. |

---

### App package (`app/`)

| File | Purpose |
|------|--------|
| **`app/__init__.py`** | Application factory: Flask app with `template_folder` and `static_folder` at project root, CORS, SQLAlchemy, JWT. Registers pages blueprint (frontend routes), API blueprints under `/api/*`, `/health`, `/uploads/<path>`, 500 handler. |

---

### Models (`app/models/`)

| File | Purpose |
|------|--------|
| **`app/models/__init__.py`** | SQLAlchemy models: **User**; **Category**, **Level**, **UserLevelProgress**; **ReadingText**, **ReadingQuestion**, **ReadingAttempt**; **ListeningAudio**, **ListeningAttempt**; **WritingTopic**, **WritingSubmission**; **SpeakingExercise**, **SpeakingAttempt**; **Feedback**; **ReelBatch**, **ReelBatchQuestion**, **ReelBatchAttempt**; **Reel**, **ReelDubbing**. |

---

### Services (`app/services/`)

| File | Purpose |
|------|--------|
| **`app/services/tts_stt.py`** | **Inclusive mode**: `text_to_speech` and `speech_to_text`. Placeholders that check `OPENAI_API_KEY`; plug in OpenAI TTS/Whisper or another provider. |
| **`app/services/feedback.py`** | `create_feedback(...)` and helpers: `generate_reading_feedback`, `generate_listening_feedback`, `generate_writing_feedback`, `generate_speaking_feedback`. |

---

### Routes (`app/routes/`)

| File | Purpose |
|------|--------|
| **`app/routes/pages.py`** | **LinguaScroll frontend (same origin):** **GET /** dashboard, **GET /lessons**, **GET /lesson**, **GET /profile**, **GET /level/<id>**. |
| **`app/routes/auth.py`** | **POST /api/auth/register**, **POST /api/auth/login** → JWT + user. **GET /api/auth/me** (JWT) → current user. |
| **`app/routes/users.py`** | **PATCH /api/users/profile** (JWT), **GET /api/users/progress** (JWT). |
| **`app/routes/categories.py`** | **GET /api/categories**, **GET /api/categories/<slug>/levels**. |
| **`app/routes/reading.py`** | **GET /api/reading/levels/<level_id>/texts**, **GET /api/reading/texts/<text_id>**, **POST /api/reading/texts/<text_id>/submit** (JWT). |
| **`app/routes/listening.py`** | **GET /api/listening/levels/<level_id>/audios**, **POST /api/listening/audios/<audio_id>/submit** (JWT). |
| **`app/routes/writing.py`** | **GET /api/writing/levels/<level_id>/topics**, **POST /api/writing/topics/<topic_id>/submit** (JWT). |
| **`app/routes/speaking.py`** | **GET /api/speaking/levels/<level_id>/exercises**, **POST /api/speaking/exercises/<exercise_id>/submit** (JWT). |
| **`app/routes/reels.py`** | **Creator (JWT):** **POST /api/reels/batches**, **POST /api/reels/upload**, **POST /api/reels/batches/<id>/question**. **Learner:** **GET /api/reels**, **GET /api/reels/batches**, **GET /api/reels/batches/<id>**, **POST /api/reels/batches/<id>/submit**. **GET /api/reels/<reel_id>/dubbing?language=**. |
| **`app/routes/tts_stt.py`** | **POST /api/tts-stt/tts** (JWT), **POST /api/tts-stt/stt** (JWT). |
| **`app/routes/feedback.py`** | **GET /api/feedback** (JWT), **GET /api/feedback/reading|<listening|writing|speaking>/<id>** (JWT). |

---

## Features

- **LinguaScroll UI**: Dashboard, lessons, and profile served at `/`, `/lessons`, `/lesson`, `/profile`. Frontend uses **`static/js/api.js`** (`LinglongAPI`) to call the same-origin API (register, login, categories, reels, etc.) and shows a backend connection status on the dashboard.
- **Four categories**: Reading (quiz), Listening (translate), Writing (essay), Speaking (read/conversation with pronunciation, fluency, dictation).
- **Levels**: Unlock next level when current level is completed (structured progression).
- **Feedback**: Stored per attempt/submission; speaking can store scores.
- **Inclusive mode**: User flag `ttsSttModeEnabled`; TTS/STT endpoints ready for API integration.
- **Reels**: Creators upload short videos; every 5 reels form a **batch** with one **question crafted from the videos’ audio**. Learners watch the 5 reels then answer the question. Optional dubbing per reel.

---

## Next steps

1. Set `OPENAI_API_KEY` and implement TTS/STT in `app/services/tts_stt.py`.
2. Add file upload for speaking audio and store URLs in `SpeakingAttempt.audio_url`.
3. Add AI-based feedback for writing and speech assessment for speaking if desired.
