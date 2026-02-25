from typing import Any, Literal

from pydantic import BaseModel, Field


class WorkflowInput(BaseModel):
    inputType: Literal["text", "voice", "image"]
    text: str | None = None
    audioUrl: str | None = None
    imageUrl: str | None = None
    sessionId: str = "default-session"


class WorkflowStatusEvent(BaseModel):
    keyword: Literal["thinking", "transcribing", "extracting", "analyzing", "creating subgoals"]
    message: str


class WorkflowOutput(BaseModel):
    normalizedQuery: dict[str, Any]
    decomposed: dict[str, Any]
    statusTrail: list[WorkflowStatusEvent] = Field(default_factory=list)
