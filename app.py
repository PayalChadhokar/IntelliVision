from flask import Flask, redirect, url_for

import os

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "intellivision-development-key"
)

app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "uploads",
    "complaints"
)

app.config["GENERATED_FOLDER"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "generated",
    "fir"
)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

os.makedirs(
    app.config["GENERATED_FOLDER"],
    exist_ok=True
)


# ============================================================
# REGISTER ROUTES
# ============================================================

from routes.auth_routes import auth_bp
from routes.complaint_routes import complaint_bp
from routes.fir_routes import fir_bp
from routes.officer_routes import officer_bp
from routes.transcription_routes import transcription_bp


app.register_blueprint(auth_bp)
app.register_blueprint(complaint_bp)
app.register_blueprint(fir_bp)
app.register_blueprint(officer_bp)
app.register_blueprint(transcription_bp)


# ============================================================
# HOME / ROOT ROUTE
# ============================================================

@app.route("/")
def home():
    return redirect(url_for("auth.login"))


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():
    return {
        "success": True,
        "application": "IntelliVision",
        "status": "running"
    }


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )