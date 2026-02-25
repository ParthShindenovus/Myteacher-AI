from __future__ import annotations

from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from ai_tutor.decomposer.repository import StateRepository
from ai_tutor.input_layer.normalizer import normalize_input
from ai_tutor.schemas.decomposer import DecomposerState
from ai_tutor.schemas.normalized_query import NormalizedQuery
from ai_tutor.services.azure_clients import AzureServiceError, build_azure_openai_llm

StatusKeyword = Literal["thinking", "transcribing", "extracting", "analyzing", "creating subgoals"]


class AgentState(TypedDict):
    input: dict[str, Any]
    normalized_query: dict[str, Any]
    decomposed: dict[str, Any]
    status_trail: list[dict[str, str]]


def _status(keyword: StatusKeyword, message: str) -> dict[str, str]:
    return {"keyword": keyword, "message": message}


def _thinking_node(state: AgentState) -> AgentState:
    statuses = [*state.get("status_trail", [])]
    statuses.append(_status("thinking", "Understanding your input format and preparing the workflow."))
    return {**state, "status_trail": statuses}


def _transcribe_node(state: AgentState) -> AgentState:
    statuses = [*state.get("status_trail", [])]
    statuses.append(_status("transcribing", "Converting your voice request into text."))
    return {**state, "status_trail": statuses}


def _extract_node(state: AgentState) -> AgentState:
    statuses = [*state.get("status_trail", [])]
    statuses.append(_status("extracting", "Extracting text and layout details from your image."))
    return {**state, "status_trail": statuses}


def _normalize_node(state: AgentState) -> AgentState:
    payload = state["input"]
    normalized = normalize_input(payload["inputType"], payload)

    statuses = [*state.get("status_trail", [])]
    statuses.append(_status("analyzing", "Analyzing the question intent and structure."))

    return {**state, "normalized_query": normalized.model_dump(), "status_trail": statuses}


def _decompose_node(state: AgentState) -> AgentState:
    normalized = NormalizedQuery(**state["normalized_query"])
    fallback_subgoals = normalized.questionParts or [normalized.query]

    try:
        llm = build_azure_openai_llm()
        structured_llm = llm.with_structured_output(DecomposerState)
        result = structured_llm.invoke(
            "Break this student question into concise learning subgoals. "
            f"Question: {normalized.query}"
        )
        decomposed = result.model_dump()
    except AzureServiceError:
        decomposed = DecomposerState(subgoals=fallback_subgoals, currentIndex=0).model_dump()

    statuses = [*state.get("status_trail", [])]
    statuses.append(_status("creating subgoals", "Creating the learning subgoals for this problem."))

    session_id = state["input"].get("sessionId", "default-session")
    try:
        StateRepository().save(session_id, decomposed)
    except Exception:
        pass

    return {**state, "decomposed": decomposed, "status_trail": statuses}


def _route_from_thinking(state: AgentState) -> str:
    input_type = state["input"]["inputType"]
    if input_type == "voice":
        return "transcribe"
    if input_type == "image":
        return "extract"
    return "normalize"


def build_tutoring_graph():
    graph = StateGraph(AgentState)

    graph.add_node("thinking", _thinking_node)
    graph.add_node("transcribe", _transcribe_node)
    graph.add_node("extract", _extract_node)
    graph.add_node("normalize", _normalize_node)
    graph.add_node("decompose", _decompose_node)

    graph.add_edge(START, "thinking")
    graph.add_conditional_edges(
        "thinking",
        _route_from_thinking,
        {
            "transcribe": "transcribe",
            "extract": "extract",
            "normalize": "normalize",
        },
    )
    graph.add_edge("transcribe", "normalize")
    graph.add_edge("extract", "normalize")
    graph.add_edge("normalize", "decompose")
    graph.add_edge("decompose", END)

    return graph.compile()
