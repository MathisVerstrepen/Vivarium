from pydantic import BaseModel, Field

class Psychology(BaseModel):
    openness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Openness to experience: creativity, curiosity, and willingness to try new things. High = imaginative, adventurous. Low = practical, conventional.",
    )
    conscientiousness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Organization, dependability, and self-discipline. High = organized, reliable, goal-oriented. Low = spontaneous, flexible, careless.",
    )
    extraversion: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Energy from social interaction. High = outgoing, talkative, assertive. Low = reserved, solitary, introspective.",
    )
    agreeableness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Tendency toward cooperation and compassion. High = trusting, helpful, empathetic. Low = competitive, skeptical, challenging.",
    )
    neuroticism: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Emotional instability and negative emotions. High = anxious, moody, easily stressed. Low = calm, emotionally stable, resilient.",
    )


class Identity(BaseModel):
    name: str
    age: int
    occupation: str
    backstory: str
    speaking_style: str


class AgentProfile(BaseModel):
    """The static definition of an Agent's soul."""

    identity: Identity
    psychology: Psychology
