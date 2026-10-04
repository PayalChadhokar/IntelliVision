# agents/state.py

from typing import Any, Dict, List, TypedDict


class InvestigationState(TypedDict, total=False):
    """
    Shared state passed between nodes of the IntelliVision
    Investigation Agent.

    The state represents one complaint being processed.
    """

    # Complaint
    complaint_id: int
    complaint_text: str

    # Speech / language
    audio_path: str
    detected_language: str
    transcription: str

    # Extracted information
    extracted_data: Dict[str, Any]

    # Crime analysis
    crime_category: str
    crime_confidence: float

    # Missing / inconsistent information
    missing_information: List[str]
    inconsistent_information: List[str]

    # Legal provisions retrieved from the database
    legal_sections: List[Dict[str, Any]]

    # FIR generation
    fir_narrative: str
    fir_data: Dict[str, Any]

    # Agent execution information
    agent_trace: List[str]

    # Workflow status
    status: str

    # Error handling
    error: str