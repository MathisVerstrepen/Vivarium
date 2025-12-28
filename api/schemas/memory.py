from pydantic import BaseModel, Field
from typing import List, Literal


class NewMemory(BaseModel):
    category: Literal["SELF", "AGENT", "WORLD"] = Field(
        ...,
        description="SELF: Facts about you. AGENT: Facts about specific other people. WORLD: General facts about the environment.",
    )
    subject: str = Field(
        ...,
        description="The specific name of the entity (e.g., 'Sophie', 'Town Square'). Use 'Self' if category is SELF.",
    )
    content: str = Field(..., description="The concise fact.")


class MemoryExtraction(BaseModel):
    """Structured extraction of knowledge at the end of a conversation."""

    memories: List[NewMemory]


class MergedMemory(BaseModel):
    """Result of a merge operation between old and new memories."""

    facts: List[str] = Field(
        ...,
        description="The resulting list of facts after merging or keeping separate.",
    )
