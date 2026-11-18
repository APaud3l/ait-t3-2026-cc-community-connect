
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "communityconnect.db")


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialise_database():
    with get_db() as db:
        with open("schema.sql", encoding="utf-8") as file:
            db.executescript(file.read())

        count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        if count == 0:
            db.executemany(
                "INSERT INTO events (title, event_date, location) VALUES (?, ?, ?)",
                [
                    ("AI Workshop", "2026-12-05", "Sydney"),
                    ("Community Networking", "2026-12-10", "Melbourne"),
                    ("Cloud Computing Seminar", "2026-12-15", "Online")
                ]
            )


@app.route("/")
def index():
    with get_db() as db:
        events = db.execute("SELECT * FROM events ORDER BY event_date").fetchall()

    return render_template("index.html", events=events)


@app.route("/register/<int:event_id>", methods=["GET", "POST"])
def register(event_id):
    with get_db() as db:
        event = db.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        ).fetchone()

        if event is None:
            return "Event not found", 404

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()

            if not name or not email:
                return "Name and email are required", 400

            db.execute(
                "INSERT INTO registrations (event_id, name, email) VALUES (?, ?, ?)",
                (event_id, name, email)
            )
            return redirect(url_for("register", event_id=event_id, success=1))

    return render_template(
        "register.html",
        event=event,
        success=request.args.get("success") == "1"
    )


if __name__ == "__main__":
    initialise_database()
    app.run(debug=True, host="127.0.0.1", port=5000)
