from flask import Blueprint, render_template, session, redirect, url_for, flash
from database.connection import get_db_connection


officer_bp = Blueprint(
    "officer",
    __name__
)


@officer_bp.route("/dashboard")
def dashboard():
    """
    Officer dashboard.

    The logged-in officer can:
    - Start a new voice complaint
    - View complaint/FIR history
    - See station information
    """

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    connection = get_db_connection()

    station = None

    if connection is not None:

        cursor = None

        try:
            cursor = connection.cursor(
                dictionary=True
            )

            station_id = session.get("station_id")

            if station_id:

                cursor.execute(
                    """
                    SELECT *
                    FROM police_stations
                    WHERE station_id = %s
                    LIMIT 1
                    """,
                    (station_id,)
                )

                station = cursor.fetchone()

        except Exception as e:

            print(
                f"[Officer Route] Station lookup error: {e}"
            )

        finally:

            if cursor:
                cursor.close()

            connection.close()

    return render_template(
        "dashboard.html",
        officer_name=session.get(
            "officer_name",
            ""
        ),
        officer_rank=session.get(
            "officer_rank",
            ""
        ),
        station=station
    )


@officer_bp.route("/history")
def history():
    """
    Complaint/FIR history for the logged-in officer.

    The history page is read-only. It does not modify
    complaints or FIR records.
    """

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    connection = get_db_connection()

    if connection is None:

        flash(
            "Unable to connect to the database.",
            "error"
        )

        return redirect(
            url_for("officer.dashboard")
        )

    cursor = None

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        station_id = session.get("station_id")

        # Get complaints together with any associated FIR
        # information.
        #
        # LEFT JOIN is used because a complaint may exist
        # before an FIR draft is generated.
        cursor.execute(
            """
            SELECT
                c.complaint_id,
                c.complainant_name,
                c.detected_language,
                c.complaint_status,
                c.created_at,
                c.updated_at,

                f.fir_id,
                f.fir_number,
                f.proposed_fir_number,
                f.police_station,
                f.district,
                f.draft_status

            FROM complaints c

            LEFT JOIN fir_drafts f
                ON c.complaint_id = f.complaint_id

            ORDER BY c.created_at DESC
            """
        )

        records = cursor.fetchall()

        return render_template(
            "history.html",
            records=records,
            complaints=records,
            officer_name=session.get(
                "officer_name",
                ""
            ),
            officer_rank=session.get(
                "officer_rank",
                ""
            )
        )

    except Exception as e:

        print(
            f"[Officer Route] History error: {e}"
        )

        flash(
            "Unable to load complaint history.",
            "error"
        )

        return redirect(
            url_for("officer.dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        connection.close()