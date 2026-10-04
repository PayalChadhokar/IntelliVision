from database.connection import get_db_connection


class Complaint:

    @staticmethod
    def create(
        complainant_name="Voice Complaint",
        original_audio_path=None,
        detected_language=None,
        original_transcription=None,
        complaint_status="RECEIVED"
    ):
        """
        Create a new complaint record.
        """

        connection = get_db_connection()

        if connection is None:
            raise RuntimeError(
                "Unable to connect to the database."
            )

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO complaints (
                    complainant_name,
                    original_audio_path,
                    detected_language,
                    original_transcription,
                    complaint_status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    complainant_name,
                    original_audio_path,
                    detected_language,
                    original_transcription,
                    complaint_status
                )
            )

            connection.commit()

            return cursor.lastrowid

        except Exception as e:

            connection.rollback()

            print(
                f"[Complaint Model] Create error: {e}"
            )

            raise

        finally:

            if cursor:
                cursor.close()

            connection.close()


    @staticmethod
    def get_by_id(complaint_id):
        """
        Retrieve one complaint by complaint_id.
        """

        connection = get_db_connection()

        if connection is None:
            raise RuntimeError(
                "Unable to connect to the database."
            )

        cursor = None

        try:
            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT *
                FROM complaints
                WHERE complaint_id = %s
                LIMIT 1
                """,
                (complaint_id,)
            )

            return cursor.fetchone()

        finally:

            if cursor:
                cursor.close()

            connection.close()


    @staticmethod
    def get_all():
        """
        Retrieve all complaints.
        """

        connection = get_db_connection()

        if connection is None:
            raise RuntimeError(
                "Unable to connect to the database."
            )

        cursor = None

        try:
            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    complaint_id,
                    complainant_name,
                    original_audio_path,
                    detected_language,
                    original_transcription,
                    complaint_status,
                    created_at,
                    updated_at
                FROM complaints
                ORDER BY created_at DESC
                """
            )

            return cursor.fetchall()

        finally:

            if cursor:
                cursor.close()

            connection.close()


    @staticmethod
    def update_status(
        complaint_id,
        complaint_status
    ):
        """
        Update complaint processing status.
        """

        connection = get_db_connection()

        if connection is None:
            raise RuntimeError(
                "Unable to connect to the database."
            )

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE complaints
                SET complaint_status = %s
                WHERE complaint_id = %s
                """,
                (
                    complaint_status,
                    complaint_id
                )
            )

            connection.commit()

            return cursor.rowcount > 0

        except Exception as e:

            connection.rollback()

            print(
                f"[Complaint Model] Status update error: {e}"
            )

            raise

        finally:

            if cursor:
                cursor.close()

            connection.close()


    @staticmethod
    def save_transcription(
        complaint_id,
        original_text,
        edited_text=None,
        detected_language=None,
        transcription_status="ORIGINAL"
    ):
        """
        Save the transcription separately.

        original_text:
            Original Whisper transcription.
            This must remain unchanged.

        edited_text:
            User/officer-edited transcription.
        """

        connection = get_db_connection()

        if connection is None:
            raise RuntimeError(
                "Unable to connect to the database."
            )

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO transcriptions (
                    complaint_id,
                    original_text,
                    edited_text,
                    detected_language,
                    transcription_status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    complaint_id,
                    original_text,
                    edited_text,
                    detected_language,
                    transcription_status
                )
            )

            connection.commit()

            return cursor.lastrowid

        except Exception as e:

            connection.rollback()

            print(
                f"[Complaint Model] Transcription save error: {e}"
            )

            raise

        finally:

            if cursor:
                cursor.close()

            connection.close()


    @staticmethod
    def get_transcription(complaint_id):
        """
        Retrieve the latest transcription record
        for a complaint.
        """

        connection = get_db_connection()

        if connection is None:
            raise RuntimeError(
                "Unable to connect to the database."
            )

        cursor = None

        try:
            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT *
                FROM transcriptions
                WHERE complaint_id = %s
                ORDER BY transcription_id DESC
                LIMIT 1
                """,
                (complaint_id,)
            )

            return cursor.fetchone()

        finally:

            if cursor:
                cursor.close()

            connection.close()