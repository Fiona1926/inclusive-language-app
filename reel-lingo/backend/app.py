from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html", title="LingLong")

    @app.get("/lessons")
    def lessons():
        return render_template("lessons.html", title="LingLong")

    @app.get("/lessons/level/<int:level_id>")
    def level(level_id):
        return render_template("lesson.html", title="LingLong", level_id=level_id, total_steps=5)

    @app.get("/profile")
    def profile():
        return render_template("profile.html", title="LingLong")

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)

