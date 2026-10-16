from flask import request
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from db import get_db_connection

app = Flask(__name__)
CORS(app)


# Home page
@app.route("/")
def home():
    return "VeerSeva Backend is Running!"


# Frontend page
@app.route("/frontend")
def frontend():
    frontend_folder = Path(__file__).resolve().parent.parent / "frontend"
    return send_from_directory(str(frontend_folder), "index.html")


# Get all welfare schemes from MySQL
@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    connection = get_db_connection()

    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                scheme_id,
                scheme_name,
                description,
                category,
                benefit,
                status
            FROM schemes
        """)

        schemes = cursor.fetchall()
        return jsonify(schemes)

    except Exception:
        app.logger.exception("Could not fetch schemes")
        return jsonify({"error": "Could not fetch schemes"}), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection.is_connected():
            connection.close()



@app.route("/api/applications", methods=["POST"])
def submit_application():
    data = request.get_json(silent=True) or {}

    applicant_name = data.get("applicant_name", "").strip()
    applicant_email = data.get("applicant_email", "").strip().lower()
    scheme_id = data.get("scheme_id")

    if not applicant_name or not applicant_email or not scheme_id:
        return jsonify({
            "error": "Name, email and welfare scheme are required"
        }), 400

    try:
        scheme_id = int(scheme_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid scheme selected"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Check that the selected scheme is active.
        cursor.execute(
            """
            SELECT scheme_id
            FROM schemes
            WHERE scheme_id = %s AND status = 'ACTIVE'
            """,
            (scheme_id,)
        )

        if cursor.fetchone() is None:
            return jsonify({
                "error": "Selected scheme is unavailable"
            }), 400

        # Find the user using their email.
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (applicant_email,)
        )
        user = cursor.fetchone()

        if user:
            user_id = user["user_id"]

            cursor.execute(
                """
                UPDATE users
                SET full_name = %s
                WHERE user_id = %s
                """,
                (applicant_name, user_id)
            )
        else:
            cursor.execute(
                """
                INSERT INTO users (full_name, email)
                VALUES (%s, %s)
                """,
                (applicant_name, applicant_email)
            )
            user_id = cursor.lastrowid

        # Save the application for this user.
        cursor.execute(
            """
            INSERT INTO applications
                (user_id, scheme_id, current_status)
            VALUES (%s, %s, %s)
            """,
            (user_id, scheme_id, "SUBMITTED")
        )

        application_id = cursor.lastrowid
        connection.commit()

        return jsonify({
            "message": "Application submitted successfully!",
            "application_id": application_id,
            "user_id": user_id,
            "status": "SUBMITTED"
        }), 201

    except Exception:
        connection.rollback()
        app.logger.exception("Application submission failed")
        return jsonify({
            "error": "Could not submit application. Check the backend logs."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection.is_connected():
            connection.close()
if __name__ == "__main__":
    app.run(debug=True)