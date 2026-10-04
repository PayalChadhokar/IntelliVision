"""
User Model
----------
Handles police officer accounts, authentication data,
and officer-to-police-station relationships.
"""

from database.connection import get_db_connection


class UserModel:

    # ============================================================
    # CREATE USER
    # ============================================================

    @staticmethod
    def create_user(
        officer_id,
        officer_name,
        officer_rank,
        username,
        password_hash,
        role="OFFICER",
        station_id=None
    ):
        """
        Create a new police officer account.
        """

        connection = get_db_connection()

        if connection is None:
            print("[UserModel] Database connection failed.")
            return None

        cursor = None

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO users (
                    officer_id,
                    officer_name,
                    officer_rank,
                    username,
                    password_hash,
                    role,
                    station_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    officer_id,
                    officer_name,
                    officer_rank,
                    username,
                    password_hash,
                    role,
                    station_id
                )
            )

            user_id = cursor.lastrowid

            connection.commit()

            print(
                f"[UserModel] User created successfully: {user_id}"
            )

            return user_id

        except Exception as e:

            connection.rollback()

            print(
                f"[UserModel] Error creating user: {e}"
            )

            return None

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # GET USER BY USERNAME
    # ============================================================

    @staticmethod
    def get_by_username(username):
        """
        Retrieve a user by username.
        """

        connection = get_db_connection()

        if connection is None:
            return None

        cursor = None

        try:

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    user_id,
                    officer_id,
                    officer_name,
                    officer_rank,
                    username,
                    password_hash,
                    role,
                    station_id,
                    created_at
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            return cursor.fetchone()

        except Exception as e:

            print(
                f"[UserModel] Error retrieving user: {e}"
            )

            return None

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # GET USER BY ID
    # ============================================================

    @staticmethod
    def get_by_id(user_id):
        """
        Retrieve a user by database user ID.
        """

        connection = get_db_connection()

        if connection is None:
            return None

        cursor = None

        try:

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    user_id,
                    officer_id,
                    officer_name,
                    officer_rank,
                    username,
                    role,
                    station_id,
                    created_at
                FROM users
                WHERE user_id = %s
                """,
                (user_id,)
            )

            return cursor.fetchone()

        except Exception as e:

            print(
                f"[UserModel] Error retrieving user: {e}"
            )

            return None

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # GET USER + STATION
    # ============================================================

    @staticmethod
    def get_user_with_station(user_id):
        """
        Retrieve officer information together with
        the police station and district associated
        with the officer.
        """

        connection = get_db_connection()

        if connection is None:
            return None

        cursor = None

        try:

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    u.user_id,
                    u.officer_id,
                    u.officer_name,
                    u.officer_rank,
                    u.username,
                    u.role,
                    u.station_id,

                    ps.station_name,
                    ps.district,
                    ps.city,
                    ps.state,
                    ps.address

                FROM users u

                LEFT JOIN police_stations ps
                    ON u.station_id = ps.station_id

                WHERE u.user_id = %s
                """,
                (user_id,)
            )

            return cursor.fetchone()

        except Exception as e:

            print(
                f"[UserModel] Error retrieving officer station: {e}"
            )

            return None

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # UPDATE USER
    # ============================================================

    @staticmethod
    def update_user(
        user_id,
        officer_name=None,
        officer_rank=None,
        station_id=None,
        role=None
    ):
        """
        Update officer account information.
        """

        connection = get_db_connection()

        if connection is None:
            return False

        cursor = None

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE users
                SET
                    officer_name = COALESCE(
                        %s,
                        officer_name
                    ),

                    officer_rank = COALESCE(
                        %s,
                        officer_rank
                    ),

                    station_id = COALESCE(
                        %s,
                        station_id
                    ),

                    role = COALESCE(
                        %s,
                        role
                    )

                WHERE user_id = %s
                """,
                (
                    officer_name,
                    officer_rank,
                    station_id,
                    role,
                    user_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        except Exception as e:

            connection.rollback()

            print(
                f"[UserModel] Error updating user: {e}"
            )

            return False

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # CHANGE PASSWORD
    # ============================================================

    @staticmethod
    def update_password(user_id, password_hash):
        """
        Update an officer's password hash.
        """

        connection = get_db_connection()

        if connection is None:
            return False

        cursor = None

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s
                WHERE user_id = %s
                """,
                (
                    password_hash,
                    user_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        except Exception as e:

            connection.rollback()

            print(
                f"[UserModel] Error updating password: {e}"
            )

            return False

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # GET ALL OFFICERS
    # ============================================================

    @staticmethod
    def get_all_users():
        """
        Retrieve all officer accounts.

        Used later by an administrator dashboard.
        """

        connection = get_db_connection()

        if connection is None:
            return []

        cursor = None

        try:

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    u.user_id,
                    u.officer_id,
                    u.officer_name,
                    u.officer_rank,
                    u.username,
                    u.role,
                    u.station_id,
                    ps.station_name,
                    ps.district,
                    u.created_at

                FROM users u

                LEFT JOIN police_stations ps
                    ON u.station_id = ps.station_id

                ORDER BY u.user_id DESC
                """
            )

            return cursor.fetchall()

        except Exception as e:

            print(
                f"[UserModel] Error retrieving users: {e}"
            )

            return []

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # DELETE USER
    # ============================================================

    @staticmethod
    def delete_user(user_id):
        """
        Delete a user account.

        This should normally be restricted to administrators.
        """

        connection = get_db_connection()

        if connection is None:
            return False

        cursor = None

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM users
                WHERE user_id = %s
                """,
                (user_id,)
            )

            connection.commit()

            return cursor.rowcount > 0

        except Exception as e:

            connection.rollback()

            print(
                f"[UserModel] Error deleting user: {e}"
            )

            return False

        finally:

            if cursor:
                cursor.close()

            connection.close()