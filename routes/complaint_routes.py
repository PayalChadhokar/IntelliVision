from flask import Blueprint, render_template, session, redirect, url_for, flash
from database.connection import get_db_connection


complaint_bp = Blueprint(
    "complaint",
    __name__,
    url_prefix="/complaint"
)


@complaint_bp.route("/new", methods=["GET"])
def new_complaint():
    """
    Opens the main IntelliVision complaint workflow.

    The complete workflow is handled from complaint.html:
        Voice Complaint
            ↓
        Transcription
            ↓
        FIR Draft
            ↓
        Officer Review
            ↓
        Approval
    """

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template(
        "complaint.html",
        officer_name=session.get("officer_name", ""),
        officer_rank=session.get("officer_rank", ""),
        station_id=session.get("station_id")
    )


@complaint_bp.route("/list", methods=["GET"])
def complaint_list():
    """
    Returns complaints received by the logged-in officer's station.
    """

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    connection = get_db_connection()

    if connection is None:
        flash("Unable to connect to the database.", "error")
        return redirect(url_for("officer.dashboard"))

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        station_id = session.get("station_id")

        cursor.execute(
            """
            SELECT
                complaint_id,
                complaint_name,
                detected_language,
                complaint_status,
                created_at,
                updated_at
            FROM complaints
            ORDER BY created_at DESC
            """,
        )

        complaints = cursor.fetchall()

        return render_template(
            "history.html",
            complaints=complaints,
            officer_name=session.get("officer_name", ""),
            officer_rank=session.get("officer_rank", "")
        )

    except Exception as e:

        print(
            f"[Complaint Route] Error retrieving complaints: {e}"
        )

        flash(
            "Unable to retrieve complaint history.",
            "error"
        )

        return redirect(url_for("officer.dashboard"))

    finally:

        if cursor:
            cursor.close()

        connection.close()