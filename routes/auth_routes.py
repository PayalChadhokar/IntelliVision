from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from database.connection import get_db_connection


# ============================================================
# AUTHENTICATION BLUEPRINT
# ============================================================

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# ============================================================
# LOGIN PAGE
# ============================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # SHOW LOGIN PAGE
    # --------------------------------------------------------

    if request.method == "GET":
        return render_template("login.html")


    # --------------------------------------------------------
    # GET LOGIN FORM DATA
    # --------------------------------------------------------

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    ).strip()


    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not username or not password:

        flash(
            "Username and password are required.",
            "error"
        )

        return render_template(
            "login.html"
        )


    # --------------------------------------------------------
    # DATABASE CONNECTION
    # --------------------------------------------------------

    connection = get_db_connection()

    if connection is None:

        flash(
            "Unable to connect to the database.",
            "error"
        )

        return render_template(
            "login.html"
        )


    cursor = None


    try:

        # ----------------------------------------------------
        # CREATE DATABASE CURSOR
        # ----------------------------------------------------

        cursor = connection.cursor(
            dictionary=True
        )


        # ----------------------------------------------------
        # GET OFFICER + POLICE STATION DETAILS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                u.user_id,
                u.officer_id,
                u.officer_name,
                u.officer_rank,
                u.username,
                u.password_hash,
                u.role,
                u.station_id,
                ps.station_name,
                ps.district
            FROM users u
            LEFT JOIN police_stations ps
                ON u.station_id = ps.station_id
            WHERE u.username = %s
            LIMIT 1
            """,
            (username,)
        )


        user = cursor.fetchone()


        # ----------------------------------------------------
        # USER NOT FOUND
        # ----------------------------------------------------

        if user is None:

            flash(
                "Invalid username or password.",
                "error"
            )

            return render_template(
                "login.html"
            )


        # ----------------------------------------------------
        # DEVELOPMENT LOGIN
        #
        # Password hashing will be added before finalization.
        # ----------------------------------------------------

        if password != user["password_hash"]:

            flash(
                "Invalid username or password.",
                "error"
            )

            return render_template(
                "login.html"
            )


        # ----------------------------------------------------
        # STORE LOGGED-IN OFFICER IN SESSION
        # ----------------------------------------------------

        session["user_id"] = user["user_id"]

        session["officer_id"] = user["officer_id"]

        session["officer_name"] = user["officer_name"]

        session["officer_rank"] = user["officer_rank"]

        session["role"] = user["role"]

        session["station_id"] = user["station_id"]

        # Police station and district come from the
        # police_stations table and are controlled by the
        # authenticated officer's station configuration.

        session["police_station"] = (
            user.get("station_name") or ""
        )

        session["district"] = (
            user.get("district") or ""
        )


        # ----------------------------------------------------
        # REDIRECT TO OFFICER DASHBOARD
        # ----------------------------------------------------

        return redirect(
            url_for(
                "officer.dashboard"
            )
        )


    # --------------------------------------------------------
    # LOGIN ERROR
    # --------------------------------------------------------

    except Exception as e:

        print(
            f"Login error: {e}"
        )

        flash(
            "An error occurred during login.",
            "error"
        )

        return render_template(
            "login.html"
        )


    # --------------------------------------------------------
    # CLOSE DATABASE RESOURCES
    # --------------------------------------------------------

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for(
            "auth.login"
        )
    )