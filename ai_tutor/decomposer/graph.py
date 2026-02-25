from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ai_tutor.schemas.decomposer import DecomposerState
from ai_tutor.schemas.normalized_query import NormalizedQuery
from ai_tutor.services.azure_clients import AzureServiceError, build_azure_openai_llm


class GraphState(TypedDict):
    normalized_query: dict
    decomposed: dict


def _decompose_node(state: GraphState) -> GraphState:
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

    return {**state, "decomposed": decomposed}


def build_decomposer_graph():
    graph = StateGraph(GraphState)
    graph.add_node("decompose", _decompose_node)
    graph.add_edge(START, "decompose")
    graph.add_edge("decompose", END)
    return graph.compile()
