# ============================================================
# CRIME CLASSIFICATION SERVICE
# ============================================================

CRIME_CATEGORIES = [
    "THEFT",
    "SNATCHING",
    "ROBBERY",
    "ASSAULT",
    "FRAUD",
    "CYBERCRIME",
    "MISSING_PERSON",
    "KIDNAPPING",
    "PROPERTY_DISPUTE",
    "HARASSMENT",
    "OTHER"
]


def classify_complaint(complaint_text):
    """
    Perform preliminary crime-category classification.

    This is a lightweight rule-based preprocessing layer.
    Final interpretation and legal-section suggestions will
    be handled by the Investigation Agent and legal database.

    The system must not treat this preliminary category as
    a final legal decision.
    """

    if not complaint_text:
        return {
            "category": "OTHER",
            "confidence": 0.0,
            "method": "preliminary_rule_based"
        }

    text = complaint_text.lower()


    # --------------------------------------------------------
    # KEYWORD GROUPS
    # --------------------------------------------------------

    keyword_groups = {

        "THEFT": [
            "stolen",
            "steal",
            "theft",
            "took my",
            "taken",
            "चोरी",
            "चोर",
            "चोरला",
            "चोरीला"
        ],

        "SNATCHING": [
            "snatched",
            "snatching",
            "snatch",
            "grabbed my phone",
            "phone snatched",
            "मोबाइल छीन",
            "मोबाईल हिसकाव"
        ],

        "ROBBERY": [
            "robbed",
            "robbery",
            "threatened me and took",
            "gunpoint",
            "weapon and took"
        ],

        "ASSAULT": [
            "assault",
            "hit me",
            "beaten",
            "beat me",
            "attacked me",
            "मारहाण",
            "मारले",
            "मारलं"
        ],

        "FRAUD": [
            "fraud",
            "cheated",
            "cheating",
            "scam",
            "deceived",
            "फसवणूक",
            "फसवले",
            "फसवणूक केली"
        ],

        "CYBERCRIME": [
            "online fraud",
            "cyber fraud",
            "otp",
            "phishing",
            "online scam",
            "upi fraud",
            "bank account hacked",
            "cyber crime"
        ],

        "MISSING_PERSON": [
            "missing person",
            "person is missing",
            "has gone missing",
            "missing since",
            "लापता",
            "बेपत्ता",
            "हरवला",
            "हरवली",
            "हरवले"
        ],

        "KIDNAPPING": [
            "kidnapped",
            "abducted",
            "kidnap",
            "kidnapping",
            "अपहरण",
            "पळवून नेले"
        ],

        "PROPERTY_DISPUTE": [
            "property dispute",
            "land dispute",
            "land ownership",
            "property boundary",
            "जमीन वाद",
            "मालमत्तेचा वाद"
        ],

        "HARASSMENT": [
            "harassment",
            "harassed",
            "threatening",
            "threatened",
            "छळ",
            "त्रास"
        ]
    }


    # --------------------------------------------------------
    # CALCULATE SIMPLE SCORES
    # --------------------------------------------------------

    scores = {}

    for category, keywords in keyword_groups.items():

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        if score > 0:
            scores[category] = score


    # --------------------------------------------------------
    # NO MATCH
    # --------------------------------------------------------

    if not scores:

        return {
            "category": "OTHER",
            "confidence": 0.0,
            "method": "preliminary_rule_based"
        }


    # --------------------------------------------------------
    # BEST PRELIMINARY CATEGORY
    # --------------------------------------------------------

    category = max(
        scores,
        key=scores.get
    )

    highest_score = scores[category]

    total_matches = sum(
        scores.values()
    )

    confidence = (
        highest_score / total_matches
        if total_matches
        else 0.0
    )


    return {
        "category": category,
        "confidence": round(
            confidence,
            2
        ),
        "matched_categories": scores,
        "method": "preliminary_rule_based"
    }