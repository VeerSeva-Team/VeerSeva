from flask import Flask
from db import get_db_connection

app = Flask(__name__)


@app.route("/")
def home():
    return "VeerSeva Backend is Running!"


@app.route("/test-db")
def test_db():
    try:
        connection = get_db_connection()
        connection.close()
        return "MySQL Database Connected Successfully!"
    except Exception as e:
        return f"Database Connection Failed: {e}"


if __name__ == "__main__":
    app.run(debug=True)