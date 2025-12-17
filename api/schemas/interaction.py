from pydantic import BaseModel, Field
from typing import Literal


class AgentOutput(BaseModel):
    """The structured response from an Agent during a turn."""

    inner_monologue: str = Field(
        ...,
        description="Your private internal thoughts. Analyze the situation, your mood, and what you want to achieve. No one hears this.",
    )
    mood: Literal[
        "Neutral",
        "Happy",
        "Angry",
        "Sad",
        "Curious",
        "Fearful",
        "Disgusted",
        "Anxious",
        "Excited",
        "Frustrated",
        "Confused",
        "Hopeful",
        "Bored",
        "Surprised",
        "Embarrassed",
        "Proud",
        "Jealous",
        "Nostalgic",
        "Relieved",
        "Suspicious",
        "Amused",
        "Contemplative",
        "Irritated",
        "Sympathetic",
    ] = Field(..., description="Your current emotional state based on the interaction.")
    speech: str = Field(
        ...,
        description="What you actually say out loud to the other person. Keep it in character.",
    )
    end_conversation: bool = Field(
        False,
        description="Set to True if you want to gracefully end the conversation.",
    )
