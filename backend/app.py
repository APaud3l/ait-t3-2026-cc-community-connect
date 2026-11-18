
import os
import re
from contextlib import closing

import mysql.connector
from flask import Flask, jsonify, request

app = Flask(__name__)


def connect_db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "communityconnect"),
        port=int(os.getenv("DB_PORT", "3306")),
        connection_timeout=5,
    )


def event_to_json(event):
    event["event_date"] = event["event_date"].isoformat()
    return event


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/api/events")
def get_events():
    try:
        with closing(connect_db()) as conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute("""
                    SELECT id, title, event_date, location
                    FROM events
                    ORDER BY event_date, id
                """)
                events = cursor.fetchall()

        return jsonify([event_to_json(e) for e in events])

    except mysql.connector.Error:
        app.logger.exception("Failed to retrieve events")
        return jsonify(error="Database unavailable"), 503


@app.get("/api/events/<int:event_id>")
def get_event(event_id):
    try:
        with closing(connect_db()) as conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute("""
                    SELECT id, title, event_date, location
                    FROM events
                    WHERE id = %s
                """, (event_id,))
                event = cursor.fetchone()

        if event is None:
            return jsonify(error="Event not found"), 404

        return jsonify(event_to_json(event))

    except mysql.connector.Error:
        app.logger.exception("Failed to retrieve event")
        return jsonify(error="Database unavailable"), 503


@app.post("/api/registrations")
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Valid JSON is required"), 400

    event_id = data.get("event_id")
    name = data.get("name")
    email = data.get("email")

    if type(event_id) is not int or event_id < 1:
        return jsonify(error="Invalid event ID"), 400

    if not isinstance(name, str) or not isinstance(email, str):
        return jsonify(error="Name and email are required"), 400

    name = name.strip()
    email = email.strip()

    if not name or len(name) > 100:
        return jsonify(error="Invalid name"), 400

    if len(email) > 255 or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email
    ):
        return jsonify(error="Invalid email address"), 400

    try:
        with closing(connect_db()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
                    INSERT INTO registrations (event_id, name, email)
                    SELECT id, %s, %s
                    FROM events
                    WHERE id = %s
                """, (name, email, event_id))

                if cursor.rowcount == 0:
                    return jsonify(error="Event not found"), 404

                registration_id = cursor.lastrowid
                conn.commit()

        return jsonify(
            id=registration_id,
            message="Registration successful!"
        ), 201

    except mysql.connector.Error:
        app.logger.exception("Failed to save registration")
        return jsonify(error="Database unavailable"), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
