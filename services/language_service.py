# ============================================================
# LANGUAGE SERVICE
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi"
}


def get_language_name(language_code):
    """
    Convert a Whisper language code into a readable language name.
    """

    if not language_code:
        return "Unknown"

    return SUPPORTED_LANGUAGES.get(
        language_code,
        language_code
    )


def is_supported_language(language_code):
    """
    Check whether the detected language is one of the
    languages currently supported by IntelliVision.
    """

    return language_code in SUPPORTED_LANGUAGES


def analyze_language(language_code):
    """
    Return structured language information for the complaint.
    """

    language_name = get_language_name(
        language_code
    )

    supported = is_supported_language(
        language_code
    )

    return {
        "code": language_code,
        "name": language_name,
        "supported": supported
    }