from typing import Any
from pydantic import BaseModel, Field


class NormalizedQuery(BaseModel):
    query: str
    subject: str = "general"
    hasDiagram: bool = False
    questionParts: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
