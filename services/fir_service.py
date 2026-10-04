import json
from datetime import datetime
from zoneinfo import ZoneInfo

from database.connection import get_db_connection


IST = ZoneInfo("Asia/Kolkata")


def _decode_json(value, default):
    """Safely decode JSON fields stored in MySQL."""
    if value is None or value == "":
        return default

    if isinstance(value, (dict, list)):
        return value

    try:
        return json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _format_date(value):
    if not value:
        return ""

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")

    return str(value)


def _format_time(value):
    if not value:
        return ""

    if isinstance(value, datetime):
        return value.strftime("%I:%M %p")

    if hasattr(value, "strftime"):
        return value.strftime("%I:%M %p")

    return str(value)


def _format_datetime(value):
    if not value:
        return ""

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %I:%M %p")

    return str(value)


# ============================================================
# CREATE FIR DRAFT
# ============================================================

def create_fir_draft(
    complaint_id,
    fir_data,
    crime_category=None,
    confidence=None,
    missing_information=None,
    inconsistent_information=None,
    structured_ai_data=None,
    agent_trace=None
):
    """
    Create and store an FIR draft.

    FIR number and FIR registration date/time are NOT assigned here.
    They are assigned only after officer approval.
    """

    connection = get_db_connection()

    if connection is None:
        raise RuntimeError("Unable to connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO fir_drafts (
                complaint_id,
                proposed_fir_number,
                district,
                police_station,
                year,
                fir_date_time,
                occurrence_from,
                occurrence_to,
                information_received_datetime,
                general_diary_reference,
                type_of_information,
                place_of_occurrence,
                complainant_name,
                father_husband_name,
                date_of_birth,
                nationality,
                uid_number,
                passport_number,
                other_id_details,
                occupation,
                complainant_address,
                phone_number,
                mobile_number,
                accused_details,
                reason_for_delay,
                property_details,
                total_property_value,
                inquest_ud_case,
                first_information_contents,
                action_taken,
                crime_category,
                crime_classification_confidence,
                missing_information,
                inconsistent_information,
                structured_ai_data,
                agent_trace,
                draft_status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, 'DRAFT'
            )
            """,
            (
                complaint_id,
                fir_data.get("proposed_fir_number"),
                fir_data.get("district"),
                fir_data.get("police_station"),
                fir_data.get("year"),
                None,  # FIR registration datetime only after approval
                fir_data.get("occurrence_from"),
                fir_data.get("occurrence_to"),
                fir_data.get("information_received_datetime"),
                fir_data.get("general_diary_reference"),
                fir_data.get("type_of_information"),
                fir_data.get("place_of_occurrence"),
                fir_data.get("complainant_name"),
                fir_data.get("father_husband_name"),
                fir_data.get("date_of_birth"),
                fir_data.get("nationality"),
                fir_data.get("uid_number"),
                fir_data.get("passport_number"),
                fir_data.get("other_id_details"),
                fir_data.get("occupation"),
                fir_data.get("complainant_address"),
                fir_data.get("phone_number"),
                fir_data.get("mobile_number"),
                fir_data.get("accused_details"),
                fir_data.get("reason_for_delay"),
                fir_data.get("property_details"),
                fir_data.get("total_property_value"),
                fir_data.get("inquest_ud_case"),
                fir_data.get("first_information_contents"),
                fir_data.get("action_taken"),
                crime_category,
                confidence,
                json.dumps(missing_information or []),
                json.dumps(inconsistent_information or []),
                json.dumps(structured_ai_data or {}),
                json.dumps(agent_trace or [])
            )
        )

        fir_id = cursor.lastrowid

        connection.commit()

        return fir_id

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# GET FIR DRAFT
# ============================================================

def get_fir_draft(fir_id):

    connection = get_db_connection()

    if connection is None:
        raise RuntimeError("Unable to connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM fir_drafts
            WHERE fir_id = %s
            LIMIT 1
            """,
            (fir_id,)
        )

        fir = cursor.fetchone()

        if not fir:
            return None

        # ----------------------------------------------------
        # Decode JSON fields
        # ----------------------------------------------------

        fir["missing_information"] = _decode_json(
            fir.get("missing_information"),
            []
        )

        fir["inconsistent_information"] = _decode_json(
            fir.get("inconsistent_information"),
            []
        )

        fir["structured_ai_data"] = _decode_json(
            fir.get("structured_ai_data"),
            {}
        )

        fir["agent_trace"] = _decode_json(
            fir.get("agent_trace"),
            []
        )

        # ----------------------------------------------------
        # Date/time display values
        # ----------------------------------------------------

        occurrence_from = fir.get("occurrence_from")
        occurrence_to = fir.get("occurrence_to")
        received_at = fir.get("information_received_datetime")
        registered_at = fir.get("fir_date_time")

        fir["occurrence_date"] = _format_date(occurrence_from)
        fir["occurrence_time"] = _format_time(occurrence_from)

        fir["occurrence_date_to"] = _format_date(occurrence_to)
        fir["occurrence_time_to"] = _format_time(occurrence_to)

        fir["information_received_date"] = _format_date(
            received_at
        )

        fir["information_received_time"] = _format_time(
            received_at
        )

        fir["information_received_datetime_display"] = (
            _format_datetime(received_at)
        )

        fir["fir_date_time_display"] = (
            _format_datetime(registered_at)
        )

        # ----------------------------------------------------
        # Convenience aliases
        # ----------------------------------------------------

        fir["property_value"] = fir.get(
            "total_property_value"
        )

        fir["property_description"] = fir.get(
            "property_details"
        )

        fir["accused_address"] = fir.get(
            "accused_details"
        )

        fir["inquest_ud_number"] = fir.get(
            "inquest_ud_case"
        )

        # ----------------------------------------------------
        # Legal provisions
        # ----------------------------------------------------

        structured_data = fir.get(
            "structured_ai_data"
        )

        if not isinstance(structured_data, dict):
            structured_data = {}

        legal_sections = structured_data.get(
            "legal_sections",
            []
        )

        if not isinstance(legal_sections, list):
            legal_sections = []

        fir["legal_sections"] = legal_sections

        # Officer-verified legal information takes precedence.
        verified_legal = structured_data.get(
            "officer_verified_legal",
            {}
        )

        if not isinstance(verified_legal, dict):
            verified_legal = {}

        if verified_legal.get("act"):
            fir["act"] = verified_legal["act"]

        elif legal_sections:
            first = legal_sections[0] or {}

            fir["act"] = (
                first.get("act_name")
                or first.get("act")
                or first.get("act_code")
                or ""
            )

        else:
            fir["act"] = ""

        if verified_legal.get("section"):
            fir["section"] = verified_legal["section"]

        elif legal_sections:
            first = legal_sections[0] or {}

            fir["section"] = (
                first.get("section_number")
                or first.get("section")
                or ""
            )

        else:
            fir["section"] = ""

        fir["act_name"] = fir.get("act", "")
        fir["section_title"] = ""

        if legal_sections:
            first = legal_sections[0] or {}

            fir["section_title"] = (
                first.get("section_title")
                or first.get("title")
                or ""
            )

        # ----------------------------------------------------
        # Frontend aliases
        # ----------------------------------------------------

        fir["father_name"] = fir.get(
            "father_husband_name"
        )

        fir["uid"] = fir.get(
            "uid_number"
        )

        fir["passport"] = fir.get(
            "passport_number"
        )

        fir["id_details"] = fir.get(
            "other_id_details"
        )

        fir["address"] = fir.get(
            "complainant_address"
        )

        fir["phone"] = fir.get(
            "phone_number"
        )

        fir["mobile"] = fir.get(
            "mobile_number"
        )

        fir["accused_name"] = fir.get(
            "accused_details"
        )

        fir["delay_reason"] = fir.get(
            "reason_for_delay"
        )

        fir["total_property_value"] = (
            fir.get("total_property_value")
        )

        fir["first_information_contents"] = (
            fir.get("first_information_contents")
            or ""
        )

        return fir

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# APPROVE FIR
# ============================================================

def approve_fir(
    fir_id,
    officer_id,
    officer_remarks="",
    edited_fields=None
):
    """
    Approve an FIR draft.

    Officer edits are saved first.

    FIR number and FIR registration datetime are generated
    only at the moment of approval.
    """

    edited_fields = edited_fields or {}

    connection = get_db_connection()

    if connection is None:
        raise RuntimeError("Unable to connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # LOCK DRAFT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                fir_id,
                year,
                proposed_fir_number,
                draft_status,
                structured_ai_data
            FROM fir_drafts
            WHERE fir_id = %s
            FOR UPDATE
            """,
            (fir_id,)
        )

        fir = cursor.fetchone()

        if fir is None:
            raise ValueError("FIR draft not found.")

        if fir["draft_status"] != "DRAFT":
            raise ValueError(
                "Only a draft FIR can be approved."
            )

        # ----------------------------------------------------
        # SAVE OFFICER-EDITABLE FIELDS
        # ----------------------------------------------------

        editable_columns = {

            "complainantName":
                "complainant_name",

            "fatherName":
                "father_husband_name",

            "fatherHusbandName":
                "father_husband_name",

            "dateOfBirth":
                "date_of_birth",

            "nationality":
                "nationality",

            "uid":
                "uid_number",

            "uidNumber":
                "uid_number",

            "passport":
                "passport_number",

            "passportNumber":
                "passport_number",

            "idDetails":
                "other_id_details",

            "otherIdDetails":
                "other_id_details",

            "occupation":
                "occupation",

            "address":
                "complainant_address",

            "complainantAddress":
                "complainant_address",

            "phone":
                "phone_number",

            "phoneNumber":
                "phone_number",

            "mobile":
                "mobile_number",

            "mobileNumber":
                "mobile_number",

            "occurrenceFrom":
                "occurrence_from",

            "occurrenceTo":
                "occurrence_to",

            "placeOfOccurrence":
                "place_of_occurrence",

            "accusedName":
                "accused_details",

            "accusedDetails":
                "accused_details",

            "accusedAddress":
                "accused_details",

            "reasonForDelay":
                "reason_for_delay",

            "delayReason":
                "reason_for_delay",

            "propertyDetails":
                "property_details",

            "propertyDescription":
                "property_details",

            "totalPropertyValue":
                "total_property_value",

            "propertyValue":
                "total_property_value",

            "firstInformationContents":
                "first_information_contents",

            "actionTaken":
                "action_taken",

            "crimeCategory":
                "crime_category"
        }

        update_parts = []
        update_values = []

        for frontend_name, db_column in editable_columns.items():

            if frontend_name not in edited_fields:
                continue

            value = edited_fields.get(
                frontend_name
            )

            if isinstance(value, str):
                value = value.strip()

            update_parts.append(
                f"{db_column} = %s"
            )

            update_values.append(value)

        if update_parts:

            update_parts.append(
                "updated_at = CURRENT_TIMESTAMP"
            )

            update_sql = f"""
                UPDATE fir_drafts
                SET
                    {", ".join(update_parts)}
                WHERE fir_id = %s
            """

            update_values.append(fir_id)

            cursor.execute(
                update_sql,
                tuple(update_values)
            )

        # ----------------------------------------------------
        # SAVE VERIFIED ACT / SECTION
        # ----------------------------------------------------

        if (
            "act" in edited_fields
            or "section" in edited_fields
        ):

            structured_data = _decode_json(
                fir.get("structured_ai_data"),
                {}
            )

            if not isinstance(structured_data, dict):
                structured_data = {}

            verified_legal = structured_data.get(
                "officer_verified_legal",
                {}
            )

            if not isinstance(verified_legal, dict):
                verified_legal = {}

            if "act" in edited_fields:
                verified_legal["act"] = str(
                    edited_fields.get("act") or ""
                ).strip()

            if "section" in edited_fields:
                verified_legal["section"] = str(
                    edited_fields.get("section") or ""
                ).strip()

            structured_data[
                "officer_verified_legal"
            ] = verified_legal

            cursor.execute(
                """
                UPDATE fir_drafts
                SET
                    structured_ai_data = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE fir_id = %s
                """,
                (
                    json.dumps(structured_data),
                    fir_id
                )
            )

        # ----------------------------------------------------
        # GET NEXT FIR NUMBER
        # ----------------------------------------------------

        year = fir["year"]

        cursor.execute(
            """
            SELECT
                COALESCE(
                    MAX(fir_number),
                    0
                ) + 1 AS next_number
            FROM fir_drafts
            WHERE year = %s
            """,
            (year,)
        )

        result = cursor.fetchone()

        next_number = result["next_number"]

        # ----------------------------------------------------
        # SYSTEM FIR REGISTRATION DATE/TIME
        # ----------------------------------------------------

        fir_registration_datetime = (
            datetime.now(IST).replace(tzinfo=None)
        )

        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE fir_drafts
            SET
                fir_number = %s,
                fir_date_time = %s,
                draft_status = 'APPROVED',
                updated_at = CURRENT_TIMESTAMP
            WHERE fir_id = %s
            """,
            (
                next_number,
                fir_registration_datetime,
                fir_id
            )
        )

        # ----------------------------------------------------
        # STORE APPROVAL
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO fir_approvals (
                fir_id,
                officer_id,
                decision,
                officer_remarks
            )
            VALUES (
                %s,
                %s,
                'APPROVED',
                %s
            )
            """,
            (
                fir_id,
                officer_id,
                officer_remarks
            )
        )

        connection.commit()

        return {
            "fir_id": fir_id,
            "fir_number": next_number,
            "status": "APPROVED",
            "approval_datetime":
                fir_registration_datetime.isoformat(),
            "fir_date_time":
                fir_registration_datetime.strftime(
                    "%d/%m/%Y %I:%M %p"
                )
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# REJECT FIR
# ============================================================

def reject_fir(
    fir_id,
    officer_id,
    officer_remarks=""
):
    """
    Reject an FIR draft.

    Rejected drafts do not receive an FIR number.
    """

    connection = get_db_connection()

    if connection is None:
        raise RuntimeError("Unable to connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                fir_id,
                draft_status
            FROM fir_drafts
            WHERE fir_id = %s
            FOR UPDATE
            """,
            (fir_id,)
        )

        fir = cursor.fetchone()

        if fir is None:
            raise ValueError(
                "FIR draft not found."
            )

        if fir["draft_status"] != "DRAFT":
            raise ValueError(
                "Only a draft FIR can be rejected."
            )

        cursor.execute(
            """
            UPDATE fir_drafts
            SET
                draft_status = 'REJECTED',
                updated_at = CURRENT_TIMESTAMP
            WHERE fir_id = %s
            """,
            (fir_id,)
        )

        cursor.execute(
            """
            INSERT INTO fir_approvals (
                fir_id,
                officer_id,
                decision,
                officer_remarks
            )
            VALUES (
                %s,
                %s,
                'REJECTED',
                %s
            )
            """,
            (
                fir_id,
                officer_id,
                officer_remarks
            )
        )

        connection.commit()

        return {
            "fir_id": fir_id,
            "status": "REJECTED"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        connection.close()