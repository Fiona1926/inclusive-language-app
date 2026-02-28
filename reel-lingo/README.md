# LinguaScroll (Flask + pure HTML/CSS/JS)

This repo now runs as a **Flask backend** that serves a **pure HTML/CSS/JS** frontend (no React, no Tailwind, no Node/Vite required).

## Run locally (Windows)

From the repo root:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
python backend\app.py
```

Then open `http://127.0.0.1:5000`.

## Project structure

- `backend/app.py`: Flask app
- `backend/templates/index.html`: HTML template
- `backend/static/index.css`: CSS
- `backend/static/main.js`: Vanilla JS (DOM code)
