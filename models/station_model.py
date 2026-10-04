"""
Police Station Model
--------------------
Handles police station and district information.
"""

from database.connection import get_db_connection


class StationModel:

    # ============================================================
    # CREATE STATION
    # ============================================================

    @staticmethod
    def create_station(
        station_name,
        district,
        city,
        state,
        address=None
    ):
        """
        Create a new police station.
        """

        connection = get_db_connection()

        if connection is None:
            print("[StationModel] Database connection failed.")
            return None

        cursor = None

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO police_stations (
                    station_name,
                    district,
                    city,
                    state,
                    address
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    station_name,
                    district,
                    city,
                    state,
                    address
                )
            )

            station_id = cursor.lastrowid

            connection.commit()

            print(
                f"[StationModel] Police station created: "
                f"{station_id}"
            )

            return station_id

        except Exception as e:

            connection.rollback()

            print(
                f"[StationModel] Error creating station: {e}"
            )

            return None

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # GET STATION
    # ============================================================

    @staticmethod
    def get_station(station_id):
        """
        Retrieve a police station by ID.
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
                    station_id,
                    station_name,
                    district,
                    city,
                    state,
                    address,
                    created_at
                FROM police_stations
                WHERE station_id = %s
                """,
                (station_id,)
            )

            return cursor.fetchone()

        except Exception as e:

            print(
                f"[StationModel] Error retrieving station: {e}"
            )

            return None

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # GET ALL STATIONS
    # ============================================================

    @staticmethod
    def get_all_stations():
        """
        Retrieve all police stations.
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
                    station_id,
                    station_name,
                    district,
                    city,
                    state,
                    address,
                    created_at
                FROM police_stations
                ORDER BY station_name
                """
            )

            return cursor.fetchall()

        except Exception as e:

            print(
                f"[StationModel] Error retrieving stations: {e}"
            )

            return []

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # UPDATE STATION
    # ============================================================

    @staticmethod
    def update_station(
        station_id,
        station_name=None,
        district=None,
        city=None,
        state=None,
        address=None
    ):
        """
        Update police station information.
        """

        connection = get_db_connection()

        if connection is None:
            return False

        cursor = None

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE police_stations
                SET
                    station_name = COALESCE(%s, station_name),
                    district = COALESCE(%s, district),
                    city = COALESCE(%s, city),
                    state = COALESCE(%s, state),
                    address = COALESCE(%s, address)
                WHERE station_id = %s
                """,
                (
                    station_name,
                    district,
                    city,
                    state,
                    address,
                    station_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        except Exception as e:

            connection.rollback()

            print(
                f"[StationModel] Error updating station: {e}"
            )

            return False

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ============================================================
    # GET STATION SUMMARY
    # ============================================================

    @staticmethod
    def get_station_summary(station_id):
        """
        Return the basic station information needed by the FIR form.

        These values are system-controlled in the FIR interface.
        """

        station = StationModel.get_station(station_id)

        if not station:
            return None

        return {
            "station_id": station["station_id"],
            "police_station": station["station_name"],
            "district": station["district"],
            "city": station["city"],
            "state": station["state"],
            "address": station["address"]
        }