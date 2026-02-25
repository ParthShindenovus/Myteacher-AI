from ai_tutor.schemas.normalized_query import NormalizedQuery
from ai_tutor.services.azure_clients import image_to_text_placeholder, speech_to_text_placeholder


def infer_subject(query: str) -> str:
    text = query.lower()
    if any(token in text for token in ["equation", "integral", "algebra", "math"]):
        return "math"
    if any(token in text for token in ["force", "velocity", "acceleration", "physics"]):
        return "physics"
    return "general"


def split_question_parts(query: str) -> list[str]:
    parts = []
    for marker in ["a)", "b)", "c)", "1.", "2.", "3."]:
        if marker in query:
            parts = [part.strip() for part in query.split(marker) if part.strip()]
            break
    return parts


def normalize_input(input_type: str, payload: dict) -> NormalizedQuery:
    if input_type == "text":
        query = payload.get("text", "").strip()
        has_diagram = False
    elif input_type == "voice":
        query = speech_to_text_placeholder(payload.get("audioUrl", "")).strip()
        has_diagram = False
    elif input_type == "image":
        query, has_diagram = image_to_text_placeholder(payload.get("imageUrl", ""))
        query = query.strip()
    else:
        raise ValueError(f"Unsupported input_type: {input_type}")

    return NormalizedQuery(
        query=query,
        subject=infer_subject(query),
        hasDiagram=has_diagram,
        questionParts=split_question_parts(query),
        metadata={"inputType": input_type},
    )
