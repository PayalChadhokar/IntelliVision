# agents/graph.py

from langgraph.graph import StateGraph, START, END

from agents.state import InvestigationState

from agents.investigation_agent import (
    extract_information_node,
    classify_crime_node,
    check_missing_information_node,
    retrieve_legal_sections_node,
    generate_fir_node,
)


def build_investigation_graph():

    workflow = StateGraph(
        InvestigationState
    )

    # Register nodes
    workflow.add_node(
        "extract_information",
        extract_information_node
    )

    workflow.add_node(
        "classify_crime",
        classify_crime_node
    )

    workflow.add_node(
        "check_missing_information",
        check_missing_information_node
    )

    workflow.add_node(
        "retrieve_legal_sections",
        retrieve_legal_sections_node
    )

    workflow.add_node(
        "generate_fir",
        generate_fir_node
    )

    # Workflow
    workflow.add_edge(
        START,
        "extract_information"
    )

    workflow.add_edge(
        "extract_information",
        "classify_crime"
    )

    workflow.add_edge(
        "classify_crime",
        "check_missing_information"
    )

    workflow.add_edge(
        "check_missing_information",
        "retrieve_legal_sections"
    )

    workflow.add_edge(
        "retrieve_legal_sections",
        "generate_fir"
    )

    workflow.add_edge(
        "generate_fir",
        END
    )

    return workflow.compile()


investigation_graph = (
    build_investigation_graph()
)