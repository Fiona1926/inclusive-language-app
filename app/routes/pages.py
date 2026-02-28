"""
Serve the frontend HTML pages (dashboard, lessons, profile).
"""
from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/", endpoint="index")
def index():
    return render_template("login.html", title="Join the Rhythm")


@pages_bp.route("/dashboard", endpoint="dashboard")
def dashboard():
    return render_template("index.html", title="Dashboard")


@pages_bp.route("/establish-aura", endpoint="establish_aura")
def establish_aura():
    return render_template("establish_aura.html", title="Establish Your Aura")


@pages_bp.route("/customize", endpoint="customize")
def customize():
    return render_template("customize.html", title="Customize Your Experience")


@pages_bp.route("/vibe", endpoint="vibe")
def vibe():
    return render_template("vibe.html", title="What's your vibe?")


@pages_bp.route("/challenge", endpoint="challenge")
def challenge():
    return render_template("challenge.html", title="Beat-Pause Challenge")


@pages_bp.route("/challenge/result", endpoint="challenge_result")
def challenge_result():
    return render_template("challenge_result.html", title="Challenge Complete")


@pages_bp.route("/lessons", endpoint="lessons")
def lessons():
    return render_template("lessons.html", title="Lessons")


@pages_bp.route("/lesson", endpoint="lesson")
def lesson():
    return render_template("lesson.html", title="Lesson", level_id=1, total_steps=5)


@pages_bp.route("/profile", endpoint="profile")
def profile():
    return render_template("profile.html", title="Profile")


@pages_bp.route("/level/<int:level_id>", endpoint="level")
def level(level_id):
    return render_template("lesson.html", title="Lesson", level_id=level_id, total_steps=5)


@pages_bp.route("/leaderboard", endpoint="leaderboard")
def leaderboard():
    return render_template("leaderboard.html", title="Leaderboard")


@pages_bp.route("/practice/partner", endpoint="practice_partner")
def practice_partner():
    return render_template("practice_incoming.html", title="Practice with Partner")


@pages_bp.route("/practice/partner/mission", endpoint="practice_partner_mission")
def practice_partner_mission():
    return render_template("practice_mission.html", title="Your Turn")


@pages_bp.route("/practice/partner/aura-check", endpoint="practice_partner_aura_check")
def practice_partner_aura_check():
    return render_template("practice_aura_check.html", title="Aura Check")


@pages_bp.route("/practice/partner/complete", endpoint="practice_partner_complete")
def practice_partner_complete():
    return render_template("practice_complete.html", title="Round Complete")
