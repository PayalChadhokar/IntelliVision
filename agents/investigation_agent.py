# agents/investigation_agent.py

from services.extraction_service import extract_information
from services.classification_service import classify_complaint
from services.missing_info_service import find_missing_information
from services.legal_services import search_legal_sections
from ai.llm import generate_response
from agents.state import InvestigationState


# =========================================================
# EXTRACT INFORMATION
# =========================================================

def extract_information_node(state: InvestigationState):

    print("[Agent] Extracting information...")

    complaint_text = state.get(
        "complaint_text",
        ""
    )

    extracted_data = extract_information(
        complaint_text
    )

    trace = list(
        state.get("agent_trace", [])
    )

    trace.append(
        "Information extraction completed."
    )

    return {
        "extracted_data": extracted_data,
        "agent_trace": trace,
        "status": "INFORMATION_EXTRACTED"
    }


# =========================================================
# CLASSIFY CRIME
# =========================================================

def classify_crime_node(state: InvestigationState):

    print("[Agent] Classifying complaint...")

    complaint_text = state.get(
        "complaint_text",
        ""
    )

    result = classify_complaint(
        complaint_text
    )

    category = result.get(
        "category",
        "OTHER"
    )

    confidence = result.get(
        "confidence",
        0.0
    )

    trace = list(
        state.get("agent_trace", [])
    )

    trace.append(
        f"Preliminary crime classification completed: {category}"
    )

    return {
        "crime_category": category,
        "crime_confidence": confidence,
        "agent_trace": trace,
        "status": "CRIME_CLASSIFIED"
    }


# =========================================================
# CHECK MISSING INFORMATION
# =========================================================

def check_missing_information_node(
    state: InvestigationState
):

    print(
        "[Agent] Checking missing information..."
    )

    extracted_data = state.get(
        "extracted_data",
        {}
    )

    # IMPORTANT:
    # find_missing_information() requires BOTH
    # extracted_data and complaint_text.
    complaint_text = state.get(
        "complaint_text",
        ""
    )

    try:

        result = find_missing_information(
            extracted_data,
            complaint_text
        )

        # -------------------------------------------------
        # Handle dictionary response
        # -------------------------------------------------

        if isinstance(result, dict):

            missing_information = result.get(
                "missing_information",
                []
            )

            inconsistent_information = result.get(
                "inconsistent_information",
                []
            )

        # -------------------------------------------------
        # Handle tuple/list response
        # -------------------------------------------------

        elif isinstance(
            result,
            (tuple, list)
        ):

            missing_information = (
                result[0]
                if len(result) > 0
                else []
            )

            inconsistent_information = (
                result[1]
                if len(result) > 1
                else []
            )

        # -------------------------------------------------
        # Fallback
        # -------------------------------------------------

        else:

            missing_information = []
            inconsistent_information = []


        trace = list(
            state.get("agent_trace", [])
        )

        trace.append(
            "Missing-information analysis completed."
        )

        return {
            "missing_information":
                missing_information or [],

            "inconsistent_information":
                inconsistent_information or [],

            "agent_trace":
                trace,

            "status":
                "MISSING_INFO_CHECKED"
        }

    except Exception as e:

        print(
            "[Agent] Missing information "
            f"analysis failed: {e}"
        )

        raise


# =========================================================
# RETRIEVE LEGAL SECTIONS
# =========================================================

def retrieve_legal_sections_node(
    state: InvestigationState
):
    """
    Retrieve relevant legal provisions from
    the MySQL legal database.

    The Agent retrieves candidate sections
    from the database.

    The LLM is NOT allowed to invent legal
    sections.

    The police officer remains responsible
    for final verification.
    """

    print(
        "[Agent] Retrieving relevant legal sections..."
    )

    crime_category = state.get(
        "crime_category",
        "OTHER"
    )

    extracted_data = state.get(
        "extracted_data",
        {}
    )

    # -------------------------------------------------
    # Extract useful keywords
    # -------------------------------------------------

    keywords = []

    property_information = extracted_data.get(
        "property_information"
    )

    if property_information:

        if isinstance(
            property_information,
            list
        ):

            keywords.extend(
                property_information
            )

        elif isinstance(
            property_information,
            str
        ):

            keywords.append(
                property_information
            )


    incident_description = extracted_data.get(
        "incident_description"
    )


    # -------------------------------------------------
    # Keyword map
    # -------------------------------------------------

    if incident_description:

        description_lower = (
            incident_description.lower()
        )


        keyword_map = {

            "snatching": [
                "snatching",
                "snatch",
                "grabbed",
                "seized",
                "took away"
            ],

            "theft": [
                "theft",
                "stolen",
                "steal"
            ],

            "robbery": [
                "robbery",
                "robbed",
                "threat",
                "force"
            ],

            "fraud": [
                "fraud",
                "cheating",
                "deception"
            ],

            "kidnapping": [
                "kidnapping",
                "kidnap",
                "abduction"
            ],

            "assault": [
                "assault",
                "hurt",
                "injury"
            ]
        }


        for keyword in keyword_map.get(
            crime_category.lower(),
            []
        ):

            if keyword in description_lower:

                keywords.append(
                    keyword
                )


    # -------------------------------------------------
    # Search legal database
    # -------------------------------------------------

    legal_sections = search_legal_sections(
        crime_category=crime_category,
        keywords=keywords
    )


    # -------------------------------------------------
    # Agent trace
    # -------------------------------------------------

    trace = list(
        state.get("agent_trace", [])
    )


    if legal_sections:

        section_numbers = [

            f"{section['act_code']} "
            f"{section['section_number']}"

            for section in legal_sections

        ]

        trace.append(
            "Legal provision retrieval completed: "
            + ", ".join(section_numbers)
        )

    else:

        trace.append(
            "Legal provision retrieval completed: "
            "no matching provision found."
        )


    return {

        "legal_sections":
            legal_sections,

        "agent_trace":
            trace,

        "status":
            "LEGAL_SECTIONS_RETRIEVED"
    }


# =========================================================
# GENERATE FIR
# =========================================================

def generate_fir_node(
    state: InvestigationState
):
    """
    Generate the AI analysis for the FIR workflow.

    IMPORTANT:

    The complainant's original transcription
    is NEVER rewritten by the LLM.

    Llama 3 is used for analysis only.

    The original complaint text is preserved
    exactly and used as First Information Contents.
    """

    print(
        "[Agent] Generating FIR analysis with Llama 3..."
    )


    complaint_text = state.get(
        "complaint_text",
        ""
    )

    extracted_data = state.get(
        "extracted_data",
        {}
    )

    crime_category = state.get(
        "crime_category",
        "OTHER"
    )

    missing_information = state.get(
        "missing_information",
        []
    )

    legal_sections = state.get(
        "legal_sections",
        []
    )


    # =====================================================
    # LEGAL CONTEXT
    # =====================================================

    legal_context = []


    for section in legal_sections:

        legal_context.append({

            "act":
                section.get(
                    "act_code"
                ),

            "act_name":
                section.get(
                    "act_name"
                ),

            "section_number":
                section.get(
                    "section_number"
                ),

            "section_title":
                section.get(
                    "section_title"
                ),

            "description":
                section.get(
                    "section_description"
                ),

            "source":
                section.get(
                    "source_name"
                )
        })


    # =====================================================
    # LLM PROMPT
    # =====================================================

    prompt = f"""
You are the AI analysis component of IntelliVision,
an Agentic AI-Based Intelligent Investigation Assistant.

Your task is to ANALYZE a complainant's statement and
assist a police officer in preparing an FIR draft.

IMPORTANT:

The original complainant statement must NEVER be rewritten,
corrected, paraphrased, summarized, or beautified.

The original statement will be preserved separately by the
application and used directly as the First Information Contents.

============================================================
ORIGINAL COMPLAINT
============================================================

{complaint_text}

============================================================
EXTRACTED INFORMATION
============================================================

{extracted_data}

============================================================
PRELIMINARY CRIME CATEGORY
============================================================

{crime_category}

Classification confidence:
{state.get("crime_confidence", 0.0)}

============================================================
MISSING INFORMATION
============================================================

{missing_information}

============================================================
LEGAL PROVISIONS RETRIEVED FROM DATABASE
============================================================

{legal_context}

============================================================
RULES
============================================================

1. Do not invent facts.

2. Do not invent names.

3. Do not invent accused persons.

4. Do not invent witnesses.

5. Do not invent dates or times.

6. Do not invent locations.

7. Do not invent monetary values.

8. Do not invent weapons or evidence.

9. Do not modify the complainant's statement.

10. Do not create new legal sections.

11. Legal provisions shown above were retrieved from the
    application's MySQL legal database.

12. Legal provisions are suggestions for officer verification.

13. Identify information that is missing or ambiguous.

14. The police officer has final authority over the FIR.

============================================================
OUTPUT
============================================================

Return only a concise analysis containing:

CRIME ANALYSIS
--------------
Explain the preliminary crime category using only facts
present in the complaint.

EXTRACTED FACTS
---------------
List the important facts that were actually stated.

MISSING INFORMATION
-------------------
List information that is required but was not provided.

LEGAL PROVISIONS
----------------
List only the legal provisions retrieved from the
application database. Do not create any new sections.

OFFICER VERIFICATION
--------------------
Mention important items that require officer verification.
"""


    # =====================================================
    # CALL LLAMA 3
    # =====================================================

    try:

        response = generate_response(
            prompt
        )


        if not response:

            raise RuntimeError(
                "Llama 3 did not return a response."
            )


        # =================================================
        # CRITICAL RULE
        # =================================================

        # NEVER use LLM output as the official
        # First Information Contents.

        fir_narrative = complaint_text


        trace = list(
            state.get("agent_trace", [])
        )


        trace.append(
            "Llama 3 complaint analysis completed."
        )


        trace.append(
            "Original complainant transcription "
            "preserved unchanged for First Information Contents."
        )


        # =================================================
        # RETURN AGENT RESULT
        # =================================================

        return {

            "fir_narrative":
                fir_narrative,

            "fir_data": {

                "llm_analysis":
                    response,

                "extracted_data":
                    extracted_data,

                "legal_sections":
                    legal_context,

                "original_complaint":
                    complaint_text,

                "first_information_contents":
                    complaint_text
            },

            "agent_trace":
                trace,

            "status":
                "DRAFT_GENERATED"
        }


    except Exception as e:

        print(
            f"[Agent] FIR analysis failed: {e}"
        )


        trace = list(
            state.get("agent_trace", [])
        )


        trace.append(
            f"FIR analysis failed: {str(e)}"
        )


        return {

            "error":
                str(e),

            "agent_trace":
                trace,

            "status":
                "ERROR"
        }