from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename

import os
import uuid

from services.speech_service import transcribe_complaint
from database.connection import get_db_connection


# ============================================================
# TRANSCRIPTION BLUEPRINT
# ============================================================

transcription_bp = Blueprint(
    "transcription",
    __name__,
    url_prefix="/transcription"
)


# ============================================================
# ALLOWED AUDIO EXTENSIONS
# ============================================================

ALLOWED_AUDIO_EXTENSIONS = {
    "wav",
    "mp3",
    "m4a",
    "webm",
    "ogg",
    "flac"
}


def allowed_audio_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_AUDIO_EXTENSIONS
    )


# ============================================================
# TRANSCRIBE AUDIO
# ============================================================

@transcription_bp.route(
    "/transcribe",
    methods=["POST"]
)
def transcribe():

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "error": "Authentication required."
        }), 401


    # --------------------------------------------------------
    # CHECK AUDIO
    # --------------------------------------------------------

    if "audio" not in request.files:

        return jsonify({
            "success": False,
            "error": "No audio file received."
        }), 400


    audio = request.files["audio"]


    if audio.filename == "":

        return jsonify({
            "success": False,
            "error": "No audio file selected."
        }), 400


    if not allowed_audio_file(audio.filename):

        return jsonify({
            "success": False,
            "error": (
                "Unsupported audio format. "
                "Use WAV, MP3, M4A, WEBM, OGG or FLAC."
            )
        }), 400


    # ========================================================
    # SAVE AUDIO
    # ========================================================

    project_root = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


    upload_folder = os.path.join(
        project_root,
        "uploads",
        "complaints"
    )


    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    original_filename = secure_filename(
        audio.filename
    )


    base, extension = os.path.splitext(
        original_filename
    )


    # UUID prevents filename collisions
    filename = (
        f"{base}_"
        f"{session['user_id']}_"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )


    audio_path = os.path.join(
        upload_folder,
        filename
    )


    audio.save(
        audio_path
    )


    # ========================================================
    # SPEECH RECOGNITION
    # ========================================================

    try:

        result = transcribe_complaint(
            audio_path
        )


        if not result:

            return jsonify({
                "success": False,
                "error": "Speech recognition returned no result."
            }), 500


        transcription = result.get(
            "text",
            ""
        ).strip()


        detected_language = result.get(
            "language"
        )


        if not transcription:

            return jsonify({
                "success": False,
                "error": (
                    "No speech could be detected "
                    "in the recording."
                )
            }), 400


        # ====================================================
        # DATABASE
        # ====================================================

        connection = get_db_connection()


        if connection is None:

            return jsonify({
                "success": False,
                "error": "Unable to connect to the database."
            }), 500


        cursor = None


        try:

            cursor = connection.cursor()


            # ------------------------------------------------
            # CREATE COMPLAINT
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO complaints (
                    complainant_name,
                    original_audio_path,
                    detected_language,
                    original_transcription,
                    complaint_status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    "Voice Complaint",
                    os.path.join(
                        "uploads",
                        "complaints",
                        filename
                    ).replace("\\", "/"),
                    detected_language,
                    transcription,
                    "TRANSCRIBED"
                )
            )


            complaint_id = cursor.lastrowid


            # ------------------------------------------------
            # CREATE TRANSCRIPTION RECORD
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO transcriptions (
                    complaint_id,
                    original_text,
                    edited_text,
                    detected_language,
                    transcription_status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    complaint_id,
                    transcription,
                    transcription,
                    detected_language,
                    "ORIGINAL"
                )
            )


            connection.commit()


        except Exception:

            connection.rollback()
            raise


        finally:

            if cursor:
                cursor.close()

            connection.close()


        # ====================================================
        # RETURN RESULT TO FRONTEND
        # ====================================================

        return jsonify({

            "success": True,

            "complaint_id": complaint_id,

            "audio_path": os.path.join(
                "uploads",
                "complaints",
                filename
            ).replace("\\", "/"),

            "transcription": transcription,

            "detected_language": detected_language

        })


    except Exception as e:

        print(
            f"Transcription error: {e}"
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500