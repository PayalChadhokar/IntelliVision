import re


def _has_value(value):
    return value is not None and str(value).strip() != ""


def _has_resolvable_relative_date(text):
    """
    Check whether the complaint contains a relative date
    that the FIR route can safely resolve.
    """
    if not text:
        return False

    text_lower = text.lower()

    relative_patterns = [
        r"\byesterday\b",
        r"\btoday\b",
        r"\btomorrow\b",
        r"\bday before yesterday\b",
        r"\bday after tomorrow\b",
    ]

    for pattern in relative_patterns:
        if re.search(pattern, text_lower):
            return True

    # Common Hindi/Marathi relative-date words.
    # These are treated as date information only when explicitly present.
    regional_patterns = [
        r"\bkal\b",
        r"\baaj\b",
        r"\baaj\s+subah\b",
        r"\bkal\s+raat\b",
    ]

    for pattern in regional_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def find_missing_information(extracted_data, complaint_text):
    """
    Identify information that is genuinely missing from the complaint.

    Relative dates such as 'yesterday' are considered available because
    the FIR generation route can resolve them into an actual date.

    The original complaint is never modified by this service.
    """

    extracted_data = extracted_data or {}
    complaint_text = complaint_text or ""

    missing = []

    # ---------------------------------------------------------
    # COMPLAINANT
    # ---------------------------------------------------------
    complainant_name = extracted_data.get("complainant_name")

    if not _has_value(complainant_name):
        missing.append("complainant_name")

    # ---------------------------------------------------------
    # OCCURRENCE DATE
    # ---------------------------------------------------------
    occurrence_date = extracted_data.get("occurrence_date")

    if not _has_value(occurrence_date):
        if not _has_resolvable_relative_date(complaint_text):
            missing.append("occurrence_date")

    # ---------------------------------------------------------
    # OCCURRENCE TIME
    # ---------------------------------------------------------
    occurrence_time = extracted_data.get("occurrence_time")

    if not _has_value(occurrence_time):
        missing.append("occurrence_time")

    # ---------------------------------------------------------
    # PLACE OF OCCURRENCE
    # ---------------------------------------------------------
    place = extracted_data.get("place_of_occurrence")

    if not _has_value(place):
        missing.append("place_of_occurrence")

    # ---------------------------------------------------------
    # INCIDENT DESCRIPTION
    # ---------------------------------------------------------
    description = (
        extracted_data.get("incident_description")
        or extracted_data.get("description")
    )

    if not _has_value(description):
        # If the complaint itself contains meaningful text,
        # it can still serve as the original incident statement.
        if len(complaint_text.strip()) < 20:
            missing.append("incident_description")

    return missing


def check_missing_information(extracted_data, complaint_text):
    """
    Backward-compatible wrapper used by the Investigation Agent.
    """
    return find_missing_information(extracted_data, complaint_text)