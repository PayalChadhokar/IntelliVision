# ============================================================
# INFORMATION EXTRACTION SERVICE
# ============================================================

import re


def _clean_value(value):
    """Clean extracted values without changing the original complaint."""
    if value is None:
        return None

    value = str(value).strip()

    value = value.strip(
        " \t\r\n.,;:!?-"
    )

    return value or None


def extract_information(text):
    """
    Extract factual information from the original complaint.

    IMPORTANT:
    - The original complaint is never modified.
    - This service does not invent missing information.
    - Extracted values are candidate values only.
    - The original transcription remains the authoritative statement.
    """

    if not text or not text.strip():
        return {}

    complaint_text = text.strip()

    # --------------------------------------------------------
    # NORMALIZED COPY FOR EXTRACTION ONLY
    # --------------------------------------------------------

    devanagari_digits = str.maketrans(
        "०१२३४५६७८९",
        "0123456789"
    )

    normalized_text = complaint_text.translate(
        devanagari_digits
    )

    lower_text = normalized_text.lower()

    extracted_data = {

        "complainant_name": None,

        "occurrence_date": None,

        "occurrence_time": None,

        "place_of_occurrence": None,

        "incident_description": complaint_text,

        "accused_information": None,

        "witness_information": None,

        "property_information": [],

        "property_description": None,

        "monetary_loss": None,

        "complainant_address": None,

        "phone_numbers": [],

        "dates": [],

        "times": [],

        "locations": []
    }

    # ========================================================
    # PHONE NUMBERS
    # ========================================================

    phone_pattern = (
        r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"
    )

    extracted_data["phone_numbers"] = list(
        dict.fromkeys(
            re.findall(
                phone_pattern,
                normalized_text
            )
        )
    )

    # ========================================================
    # EXACT DATE PATTERNS
    # ========================================================

    date_patterns = [

        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"
    ]

    for pattern in date_patterns:

        matches = re.findall(
            pattern,
            normalized_text
        )

        extracted_data["dates"].extend(
            matches
        )

    extracted_data["dates"] = list(
        dict.fromkeys(
            extracted_data["dates"]
        )
    )

    if extracted_data["dates"]:

        extracted_data["occurrence_date"] = (
            extracted_data["dates"][0]
        )

    # ========================================================
    # RELATIVE DATE
    # ========================================================

    relative_date_patterns = [

        r"\byesterday\b",

        r"\btoday\b",

        r"\btomorrow\b",

        r"\blast night\b",

        r"\bthis morning\b",

        r"\blast evening\b",

        r"\baaj\b",

        r"\bkal\b"
    ]

    # Only use relative date when no explicit date
    # was already found.

    if not extracted_data["occurrence_date"]:

        for pattern in relative_date_patterns:

            match = re.search(
                pattern,
                normalized_text,
                flags=re.IGNORECASE
            )

            if match:

                extracted_data[
                    "occurrence_date"
                ] = match.group(0)

                break

    # ========================================================
    # TIME
    # ========================================================

    time_patterns = [

        r"\b\d{1,2}(?::\d{2})?\s?"
        r"(?:AM|PM|am|pm)\b",

        r"\b\d{1,2}(?::\d{2})?\s?"
        r"(?:baje|vajta)\b"
    ]

    time_candidates = []

    for pattern in time_patterns:

        time_candidates.extend(
            re.findall(
                pattern,
                normalized_text,
                flags=re.IGNORECASE
            )
        )

    extracted_data["times"] = list(
        dict.fromkeys(
            time_candidates
        )
    )

    if extracted_data["times"]:

        extracted_data["occurrence_time"] = (
            extracted_data["times"][0]
        )

    # ========================================================
    # LOCATION EXTRACTION
    # ========================================================

    location_patterns = [

        r"\bnear\s+"
        r"([A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*)*"
        r"(?:,\s*[A-Z][A-Za-z]+)?)",

        r"\bat\s+"
        r"([A-Z][A-Za-z0-9]*(?:\s+[A-Za-z0-9]+)*"
        r"(?:,\s*[A-Z][A-Za-z]+)?)",

        r"\boutside\s+"
        r"([A-Z][A-Za-z0-9]*(?:\s+[A-Za-z0-9]+)*"
        r"(?:,\s*[A-Z][A-Za-z]+)?)",

        r"\binside\s+"
        r"([A-Z][A-Za-z0-9]*(?:\s+[A-Za-z0-9]+)*"
        r"(?:,\s*[A-Z][A-Za-z]+)?)"
    ]

    location_candidates = []

    for pattern in location_patterns:

        matches = re.findall(
            pattern,
            complaint_text
        )

        for match in matches:

            location = _clean_value(match)

            if not location:
                continue

            # Remove common sentence continuations.
            location = re.split(
                r"\.\s+|\s+(?:while|when|where|and then)\s+",
                location,
                maxsplit=1,
                flags=re.IGNORECASE
            )[0]

            ignored_locations = {
                "home",
                "there",
                "here",
                "my house"
            }

            if location.lower() not in ignored_locations:

                location_candidates.append(
                    location
                )

    extracted_data["locations"] = list(
        dict.fromkeys(
            location_candidates
        )
    )

    if extracted_data["locations"]:

        extracted_data["place_of_occurrence"] = (
            extracted_data["locations"][0]
        )

    # ========================================================
    # COMPLAINANT NAME
    # ========================================================

    # Capture the name only until punctuation or a sentence
    # boundary. This prevents:
    #
    # "My name is Payal Chadhokar. Yesterday..."
    #
    # from becoming:
    #
    # "Payal Chadhokar Yesterday"

    name_patterns = [

        r"\bmy\s+name\s+is\s+"
        r"([A-Za-z]+(?:\s+[A-Za-z]+){0,2})"
        r"(?=[\.,!?;:]|\s+(?:and|i|yesterday|today|"
        r"tomorrow|on|was|am|is|at|from|living)\b|$)",

        r"\bi\s+am\s+"
        r"([A-Za-z]+(?:\s+[A-Za-z]+){0,2})"
        r"(?=[\.,!?;:]|\s+(?:and|i|yesterday|today|"
        r"tomorrow|on|was|am|is|at|from|living)\b|$)"
    ]

    for pattern in name_patterns:

        match = re.search(
            pattern,
            complaint_text,
            flags=re.IGNORECASE
        )

        if match:

            name = _clean_value(
                match.group(1)
            )

            if name:

                extracted_data[
                    "complainant_name"
                ] = name

                break

    # ========================================================
    # ADDRESS
    # ========================================================

    address_patterns = [

        r"\bi\s+live\s+at\s+(.+?)(?:\.|,?\s+i\s+was\b)",

        r"\bmy\s+address\s+is\s+(.+?)(?:\.|$)",

        r"\bliving\s+at\s+(.+?)(?:\.|$)"
    ]

    for pattern in address_patterns:

        match = re.search(
            pattern,
            complaint_text,
            flags=re.IGNORECASE
        )

        if match:

            extracted_data[
                "complainant_address"
            ] = _clean_value(
                match.group(1)
            )

            break

    # ========================================================
    # PROPERTY / ITEM INFORMATION
    # ========================================================

    property_keywords = [
        "mobile phone",
        "mobile",
        "phone",
        "laptop",
        "wallet",
        "bag",
        "jewellery",
        "jewelry",
        "watch",
        "purse",
        "tablet",
        "computer",

        "मोबाइल",
        "फोन",
        "पर्स",
        "बैग"
    ]

    found_properties = []

    for keyword in property_keywords:

        if keyword.lower() in lower_text:

            found_properties.append(
                keyword
            )

    found_properties = list(
        dict.fromkeys(
            found_properties
        )
    )

    extracted_data[
        "property_information"
    ] = found_properties

    # --------------------------------------------------------
    # PROPERTY DESCRIPTION
    # --------------------------------------------------------

    property_patterns = [

        r"\b(?:a|an|the)\s+"
        r"([A-Z][A-Za-z0-9]*(?:\s+[A-Za-z0-9-]+){0,5})"
        r"\s+(?:mobile phone|mobile|phone|laptop|wallet|"
        r"watch|bag|purse|tablet|computer)\b",

        r"\b(?:my|a|an|the)\s+"
        r"([A-Za-z0-9]+(?:\s+[A-Za-z0-9-]+){0,5})"
        r"\s+(?:mobile phone|mobile|phone|laptop|wallet|"
        r"watch|bag|purse|tablet|computer)\b"
    ]

    for pattern in property_patterns:

        match = re.search(
            pattern,
            complaint_text,
            flags=re.IGNORECASE
        )

        if match:

            description = _clean_value(
                match.group(1)
            )

            if description:

                extracted_data[
                    "property_description"
                ] = description

                break

    # --------------------------------------------------------
    # FALLBACK PROPERTY DESCRIPTION
    # --------------------------------------------------------

    if (
        not extracted_data[
            "property_description"
        ]
        and found_properties
    ):

        extracted_data[
            "property_description"
        ] = ", ".join(
            found_properties
        )

    # ========================================================
    # MONETARY LOSS
    # ========================================================

    money_patterns = [

        r"(?:₹|rs\.?|inr)\s*"
        r"(\d+(?:,\d{3})*(?:\.\d+)?)",

        r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*"
        r"(?:rupees|rs\.?|inr)"
    ]

    money_values = []

    for pattern in money_patterns:

        matches = re.findall(
            pattern,
            complaint_text,
            flags=re.IGNORECASE
        )

        money_values.extend(
            matches
        )

    # Support:
    #
    # "worth about 25000 rupees"
    # "worth approximately 25000 rupees"

    worth_pattern = (
        r"\bworth\s+"
        r"(?:about\s+|approximately\s+|around\s+)?"
        r"(\d+(?:,\d{3})*(?:\.\d+)?)"
        r"\s*(?:rupees|rs\.?|inr)"
    )

    worth_matches = re.findall(
        worth_pattern,
        complaint_text,
        flags=re.IGNORECASE
    )

    money_values.extend(
        worth_matches
    )

    if money_values:

        extracted_data[
            "monetary_loss"
        ] = money_values[0].replace(
            ",",
            ""
        )

    # ========================================================
    # RETURN STRUCTURED INFORMATION
    # ========================================================

    return extracted_data


# ============================================================
# BACKWARD-COMPATIBILITY HELPER
# ============================================================

def extract_basic_entities(text):
    """
    Compatibility wrapper for older parts of IntelliVision.
    """

    data = extract_information(text)

    return {
        "names": (
            [data["complainant_name"]]
            if data.get("complainant_name")
            else []
        ),

        "phone_numbers": data.get(
            "phone_numbers",
            []
        ),

        "dates": data.get(
            "dates",
            []
        ),

        "times": data.get(
            "times",
            []
        ),

        "locations": data.get(
            "locations",
            []
        )
    }