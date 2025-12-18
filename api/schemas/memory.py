from pydantic import BaseModel, Field
from typing import List


class MemoryExtraction(BaseModel):
    """Structured extraction of knowledge at the end of a conversation."""

    facts: List[str] = Field(
        ...,
        description="A list of distinct, objective facts learned about the world or the other person (e.g., 'Sophie hates rain', 'Marcus studies engineering').",
    )
