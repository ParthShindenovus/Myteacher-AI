from pydantic import BaseModel, Field


class DecomposerState(BaseModel):
    subgoals: list[str] = Field(default_factory=list)
    currentIndex: int = 0
