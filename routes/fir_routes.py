# ============================================================
# INTELLIVISION
# FIR ROUTES
# ============================================================

from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
import re

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
)

from agents.graph import investigation_graph

from services.fir_service import (
    create_fir_draft,
    get_fir_draft,
    approve_fir,
    reject_fir,
)


# ============================================================
# BLUEPRINT
# ============================================================

fir_bp = Blueprint(
    "fir",
    __name__,
    url_prefix="/fir"
)


# ============================================================
# TIMEZONE
# ============================================================

IST = ZoneInfo("Asia/Kolkata")


# ============================================================
# RELATIVE DATE CONVERTER
# ============================================================

def resolve_relative_date(value):
    """
    Convert natural-language relative dates into actual dates.

    Examples:
        today -> current date
        yesterday -> current date - 1 day
        tomorrow -> current date + 1 day
        day before yesterday -> current date - 2 days

    Returns:
        datetime.date or None
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    text = str(value).strip().lower()

    if not text:
        return None

    today = datetime.now(IST).date()

    # --------------------------------------------------------
    # RELATIVE DATES
    # --------------------------------------------------------

    # Unambiguous "today" forms.
    if text in {
        "today",
        "aaj",
        "आज",
    }:
        return today

    # "kal" / "कल" is ambiguous in Hindi/Marathi (yesterday or tomorrow),
    # so it is deliberately NOT converted without additional context.
    if text in {
        "yesterday",
        "yday",
    }:
        return today - timedelta(days=1)

    if text in {
        "tomorrow",
    }:
        return today + timedelta(days=1)

    if text in {
        "day before yesterday",
        "day-before-yesterday",
    }:
        return today - timedelta(days=2)

    # --------------------------------------------------------
    # COMMON EXPLICIT DATE FORMATS
    # --------------------------------------------------------

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d-%m-%y",
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                text,
                fmt
            ).date()

        except ValueError:
            continue

    # --------------------------------------------------------
    # WORD-BASED MONTH FORMATS
    # --------------------------------------------------------

    month_formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%B %d %Y",
        "%b %d %Y",
    ]

    for fmt in month_formats:

        try:
            return datetime.strptime(
                text,
                fmt
            ).date()

        except ValueError:
            continue

    # --------------------------------------------------------
    # UNRESOLVED DATE
    # --------------------------------------------------------

    return None


# ============================================================
# TIME CONVERTER
# ============================================================

def resolve_time(value):
    """
    Convert extracted natural-language time into datetime.time.

    Examples:
        8 PM -> 20:00
        8:30 PM -> 20:30
        20:00 -> 20:00

    Returns:
        datetime.time or None
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.time()

    if isinstance(value, time):
        return value

    text = str(value).strip()

    if not text:
        return None

    # Remove common trailing punctuation.
    text = text.rstrip(".,;")

    # Whisper can return Devanagari digits.
    text = text.translate(
        str.maketrans("०१२३४५६७८९", "0123456789")
    )

    # Common Hindi/Marathi spoken-time forms.
    spoken_match = re.search(
        r"(?:सुबह|दोपहर|शाम|रात|सकाळी|दुपारी|संध्याकाळी|रात्री)?\s*"
        r"(\d{1,2})(?::(\d{2}))?\s*(?:बजे|वाजता)?",
        text,
        flags=re.IGNORECASE
    )

    if spoken_match and ("बजे" in text or "वाजता" in text or any(
        word in text for word in ["सुबह", "दोपहर", "शाम", "रात", "सकाळी", "दुपारी", "संध्याकाळी", "रात्री"]
    )):
        hour = int(spoken_match.group(1))
        minute = int(spoken_match.group(2) or 0)

        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            return None

        if any(word in text for word in ["रात", "रात्री"]):
            if 1 <= hour < 12:
                hour += 12
        elif any(word in text for word in ["दोपहर", "शाम", "दुपारी", "संध्याकाळी"]):
            if 1 <= hour < 12:
                hour += 12
        elif any(word in text for word in ["सुबह", "सकाळी"]):
            if hour == 12:
                hour = 0

        return time(hour, minute)

    formats = [
        "%I %p",
        "%I:%M %p",
        "%I:%S %p",
        "%I%p",
        "%I:%M%p",
        "%H:%M",
        "%H:%M:%S",
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                text.upper(),
                fmt
            ).time()

        except ValueError:
            continue

    return None


# ============================================================
# BUILD OCCURRENCE DATETIME
# ============================================================

def build_occurrence_datetime(
    occurrence_date_value,
    occurrence_time_value
):
    """
    Build a MySQL-compatible datetime from extracted
    occurrence date and time.

    Relative dates are resolved using the current IST date.

    If the date cannot be safely resolved, None is returned.
    """

    resolved_date = resolve_relative_date(
        occurrence_date_value
    )

    if resolved_date is None:
        return None

    resolved_time = resolve_time(
        occurrence_time_value
    )

    # --------------------------------------------------------
    # If time exists, combine date + time.
    # --------------------------------------------------------

    if resolved_time is not None:

        return datetime.combine(
            resolved_date,
            resolved_time
        )

    # --------------------------------------------------------
    # If only the date is known, store midnight.
    #
    # The officer can edit the occurrence time later.
    # --------------------------------------------------------

    return datetime.combine(
        resolved_date,
        time.min
    )


# ============================================================
# RUN INVESTIGATION AGENT
# ============================================================

@fir_bp.route(
    "/generate",
    methods=["POST"]
)
def generate_fir():

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "error": "Authentication required."
        }), 401


    # --------------------------------------------------------
    # REQUEST DATA
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "error": "No complaint data received."
        }), 400


    complaint_id = data.get(
        "complaint_id"
    )


    # --------------------------------------------------------
    # ACCEPT FRONTEND TRANSCRIPTION
    # --------------------------------------------------------

    complaint_text = str(
    data.get(
        "transcription",
        data.get(
            "complaint_text",
            ""
        )
    ) or ""
).strip()


    # --------------------------------------------------------
    # VALIDATE COMPLAINT ID
    # --------------------------------------------------------

    if not complaint_id:

        return jsonify({
            "success": False,
            "error": "Complaint ID is required."
        }), 400


    # --------------------------------------------------------
    # VALIDATE COMPLAINT TEXT
    # --------------------------------------------------------

    if not complaint_text:

        return jsonify({
            "success": False,
            "error": "Complaint text is required."
        }), 400


    try:

        # ====================================================
        # RUN LANGGRAPH INVESTIGATION AGENT
        # ====================================================

        result = investigation_graph.invoke({

            "complaint_id": complaint_id,

            "complaint_text": complaint_text,

            "agent_trace": [],

        })


        # ----------------------------------------------------
        # AGENT ERROR
        # ----------------------------------------------------

        if result.get("status") == "ERROR":

            return jsonify({

                "success": False,

                "error": result.get(
                    "error",
                    "Investigation Agent failed."
                )

            }), 500


        # ====================================================
        # EXTRACT AGENT RESULT
        # ====================================================

        extracted_data = result.get(
            "extracted_data",
            {}
        )


        crime_category = result.get(
            "crime_category",
            "OTHER"
        )


        crime_confidence = result.get(
            "crime_confidence",
            0.0
        )


        missing_information = result.get(
            "missing_information",
            []
        )


        inconsistent_information = result.get(
            "inconsistent_information",
            []
        )


        fir_narrative = result.get(
            "fir_narrative",
            ""
        )


        legal_sections = result.get(
            "legal_sections",
            []
        )


        agent_trace = result.get(
            "agent_trace",
            []
        )


        # ====================================================
        # EXTRACT OCCURRENCE DATE AND TIME
        # ====================================================

        occurrence_date_value = extracted_data.get(
            "occurrence_date"
        )


        occurrence_time_value = extracted_data.get(
            "occurrence_time"
        )


        occurrence_datetime = build_occurrence_datetime(

            occurrence_date_value,

            occurrence_time_value

        )


        # ====================================================
        # EXTRACT COMPLAINANT PHONE
        # ====================================================

        phone_numbers = extracted_data.get(
            "phone_numbers",
            []
        )


        complainant_phone = (

            phone_numbers[0]

            if phone_numbers

            else None

        )


        # ====================================================
        # PROPERTY DETAILS
        # ====================================================

        property_information = extracted_data.get(
            "property_information",
            []
        )


        if property_information:

            property_details = ", ".join(
                str(item)
                for item in property_information
            )

        else:

            property_details = None


        # ====================================================
        # MONETARY VALUE
        # ====================================================

        monetary_loss = extracted_data.get(
            "monetary_loss"
        )


        # ====================================================
        # FIR DATA
        # ====================================================

        fir_data = {

            # ------------------------------------------------
            # SYSTEM CONTROLLED
            # ------------------------------------------------

            "proposed_fir_number": None,

            "district": session.get("district", "Nagpur City"),
            
            "police_station": session.get("police_station", "Hingna Police Station"),

            "year": datetime.now(IST).year,

            "fir_date_time": None,

            "information_received_datetime": datetime.now(
                IST
            ).replace(
                tzinfo=None
            ),


            # ------------------------------------------------
            # OCCURRENCE
            # ------------------------------------------------

            "occurrence_from": occurrence_datetime,

            "occurrence_to": None,


            # ------------------------------------------------
            # GENERAL FIR INFORMATION
            # ------------------------------------------------

            "general_diary_reference": None,

            "type_of_information": "Oral",


            # ------------------------------------------------
            # PLACE
            # ------------------------------------------------

            "place_of_occurrence": extracted_data.get(
                "place_of_occurrence"
            ),


            # ------------------------------------------------
            # COMPLAINANT
            # ------------------------------------------------

            "complainant_name": extracted_data.get(
                "complainant_name"
            ),

            "father_husband_name": None,

            "date_of_birth": None,

            "nationality": None,

            "uid_number": None,

            "passport_number": None,

            "other_id_details": None,

            "occupation": None,

            "complainant_address": extracted_data.get(
                "complainant_address"
            ),

            "phone_number": complainant_phone,

            "mobile_number": complainant_phone,


            # ------------------------------------------------
            # ACCUSED
            # ------------------------------------------------

            "accused_details": extracted_data.get(
                "accused_information"
            ),


            # ------------------------------------------------
            # DELAY
            # ------------------------------------------------

            "reason_for_delay": None,


            # ------------------------------------------------
            # PROPERTY
            # ------------------------------------------------

            "property_details": property_details,

            "total_property_value": monetary_loss,


            # ------------------------------------------------
            # INQUEST
            # ------------------------------------------------

            "inquest_ud_case": None,


            # ------------------------------------------------
            # FIR CONTENT
            # ------------------------------------------------

            "first_information_contents": fir_narrative,

            "action_taken": None,

        }


        # ====================================================
        # STORE FIR DRAFT
        # ====================================================

        # Store the complete Agent output, including the legal provisions.
        # The database has one JSON field for this structured AI result, so
        # we keep legal_sections inside it instead of losing them.
        structured_ai_data = result.get("fir_data") or {}
        if not isinstance(structured_ai_data, dict):
            structured_ai_data = {}

        structured_ai_data["legal_sections"] = legal_sections or []
        structured_ai_data["extracted_data"] = extracted_data or {}
        structured_ai_data["complaint_text"] = complaint_text
        structured_ai_data["fir_narrative"] = fir_narrative

        fir_id = create_fir_draft(
            complaint_id=complaint_id,
            fir_data=fir_data,
            crime_category=crime_category,
            confidence=crime_confidence,
            missing_information=missing_information or None,
            inconsistent_information=inconsistent_information or None,
            structured_ai_data=structured_ai_data,
            agent_trace=agent_trace,
        )


        # ====================================================
        # RETURN SUCCESS
        # ====================================================

        saved_draft = get_fir_draft(fir_id)
        if saved_draft is None:
            return jsonify({
                "success": False,
                "error": "FIR draft was created but could not be retrieved."
            }), 500

        # Add logged-in officer details to the response without storing
        # them as editable FIR facts. They come from the authenticated session.
        saved_draft["officer_name"] = session.get("officer_name", "")
        saved_draft["officer_rank"] = session.get("officer_rank", "")
        saved_draft["officer_id"] = session.get("officer_id", "")
        saved_draft["legal_sections"] = legal_sections or saved_draft.get("legal_sections", [])

        # Prefer officer-verified legal data; otherwise use the first
        # provision retrieved from the MySQL legal database.
        structured_data = saved_draft.get("structured_ai_data") or {}
        verified_legal = structured_data.get("officer_verified_legal", {})
        if not isinstance(verified_legal, dict):
            verified_legal = {}

        if verified_legal.get("act") or verified_legal.get("section"):
            saved_draft["act"] = verified_legal.get("act", "")
            saved_draft["section"] = verified_legal.get("section", "")
        elif saved_draft["legal_sections"]:
            first = saved_draft["legal_sections"][0] or {}
            saved_draft["act"] = (
                first.get("act") or first.get("act_code") or first.get("act_name") or ""
            )
            saved_draft["section"] = (
                first.get("section_number") or first.get("section") or ""
            )

        return jsonify({
            "success": True,

            "fir_id": fir_id,

            "fir": saved_draft,

            "fir_data": saved_draft,

    "crime_category":
        result.get(
            "crime_category"
        ),

    "confidence":
        result.get(
            "crime_classification_confidence"
        ),

    "missing_information":
        result.get(
            "missing_information",
            []
        ),

    "inconsistent_information":
        result.get(
            "inconsistent_information",
            []
        ),

    "legal_sections":
        result.get(
            "legal_sections",
            []
        ),

    "message":
        "FIR draft generated successfully."
})

    except Exception as e:

        print(
            f"FIR generation error: {e}"
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# FIR DRAFT PAGE
# ============================================================

@fir_bp.route(
    "/draft/<int:fir_id>"
)
def draft(fir_id):

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )


    try:

        fir = get_fir_draft(
            fir_id
        )


        if fir is None:

            return (
                "FIR draft not found.",
                404
            )


        return render_template(
            "fir_draft.html",
            fir=fir
        )


    except Exception as e:

        print(
            f"FIR draft loading error: {e}"
        )

        return (
            "Unable to load FIR draft.",
            500
        )


# ============================================================
# APPROVE FIR
# ============================================================

@fir_bp.route(
    "/approve/<int:fir_id>",
    methods=["POST"]
)
def approve(fir_id):

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "error": "Authentication required."
        }), 401

    officer_id = session.get("user_id")

    data = request.get_json(
        silent=True
    ) or {}

    officer_remarks = str(
        data.get(
            "officer_remarks",
            ""
        ) or ""
    ).strip()

    # --------------------------------------------------------
    # RECEIVE OFFICER-EDITED FIR FIELDS
    # --------------------------------------------------------

    editable_fields = {}

    allowed_fields = [
    "complainantName",

    "fatherName",
    "fatherHusbandName",

    "dateOfBirth",
    "nationality",

    "uid",
    "uidNumber",

    "passport",
    "passportNumber",

    "idDetails",
    "otherIdDetails",

    "occupation",

    "address",
    "complainantAddress",

    "phone",
    "phoneNumber",

    "mobile",
    "mobileNumber",

    "occurrenceFrom",
    "occurrenceTo",

    "placeOfOccurrence",

    "accusedName",
    "accusedDetails",
    "accusedAddress",

    "reasonForDelay",
    "delayReason",

    "propertyDetails",
    "propertyDescription",

    "totalPropertyValue",
    "propertyValue",

    "firstInformationContents",

    "actionTaken",

    "crimeCategory",

    "act",
    "section"
]

    for field in allowed_fields:

        if field in data:
            editable_fields[field] = data[field]

    try:

        result = approve_fir(
            fir_id=fir_id,
            officer_id=officer_id,
            officer_remarks=officer_remarks,
            edited_fields=editable_fields
        )

        return jsonify({
            "success": True,
            "approval": result,
            "fir_id": result.get("fir_id"),
            "fir_number": result.get("fir_number"),
            "status": result.get("status"),
            "approval_datetime": result.get("approval_datetime"),
            "fir_date_time": result.get("fir_date_time"),
            "message": "FIR approved successfully."
        })

    except Exception as e:

        print(
            f"FIR approval error: {e}"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ============================================================
# REJECT FIR
# ============================================================

@fir_bp.route(
    "/reject/<int:fir_id>",
    methods=["POST"]
)
def reject(fir_id):

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "error": "Authentication required."

        }), 401


    officer_id = session.get(
        "user_id"
    )


    data = request.get_json(
        silent=True
    ) or {}


    officer_remarks = str(
        data.get(
            "officer_remarks",
            ""
        ) or ""
    ).strip()


    try:

        result = reject_fir(

            fir_id=fir_id,

            officer_id=officer_id,

            officer_remarks=officer_remarks

        )


        return jsonify({

            "success": True,

            "approval": result

        })


    except Exception as e:

        print(
            f"FIR rejection error: {e}"
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500