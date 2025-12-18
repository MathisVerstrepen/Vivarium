from pydantic import BaseModel, Field
from typing import Literal, List


class Psychology(BaseModel):
    """The Big Five (OCEAN) Model."""

    openness: float = Field(
        ..., ge=0.0, le=1.0, description="Creativity and curiosity."
    )
    conscientiousness: float = Field(
        ..., ge=0.0, le=1.0, description="Discipline and organization."
    )
    extraversion: float = Field(
        ..., ge=0.0, le=1.0, description="Social energy and assertiveness."
    )
    agreeableness: float = Field(
        ..., ge=0.0, le=1.0, description="Compassion and cooperation."
    )
    neuroticism: float = Field(
        ..., ge=0.0, le=1.0, description="Emotional instability and anxiety."
    )


class MoralCompass(BaseModel):
    """Moral Foundations Theory (0.0 = Indifferent, 1.0 = Absolute Value)."""

    care_harm: float = Field(
        ..., ge=0.0, le=1.0, description="Sensitivity to suffering/kindness."
    )
    fairness_cheating: float = Field(
        ..., ge=0.0, le=1.0, description="Focus on justice and reciprocity."
    )
    loyalty_betrayal: float = Field(
        ..., ge=0.0, le=1.0, description="Focus on group cohesion and patriotism."
    )
    authority_subversion: float = Field(
        ..., ge=0.0, le=1.0, description="Respect for hierarchy and tradition."
    )
    sanctity_degradation: float = Field(
        ..., ge=0.0, le=1.0, description="Focus on purity, sanctity, or religiousness."
    )


class EmotionalProfile(BaseModel):
    base_mood: str = Field(
        ..., description="Default emotional state (e.g., 'Melancholic', 'Optimistic')."
    )
    emotional_volatility: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How easily their mood changes (0=Stoic, 1=Unstable).",
    )
    attachment_style: Literal[
        "Secure", "Anxious-Preoccupied", "Dismissive-Avoidant", "Fearful-Avoidant"
    ]
    triggers: List[str] = Field(
        default_factory=list,
        description="Specific topics or events that cause strong reactions.",
    )


class Cognition(BaseModel):
    decision_basis: Literal["Logic", "Emotion", "Intuition", "Tradition"]
    impulsivity: float = Field(
        ..., ge=0.0, le=1.0, description="0 = Over-analyzer, 1 = Acts without thinking."
    )


class CommunicationStyle(BaseModel):
    verbosity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.0 = One word answers. 0.5 = Normal. 1.0 = Long monologues.",
    )
    formality: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.0 = Heavy slang/swear words. 1.0 = Academic/Victorian.",
    )
    tone: str = Field(
        ..., description="E.g., 'Sarcastic', 'Gentle', 'Aggressive', 'Dry'."
    )


class Identity(BaseModel):
    name: str
    age: int
    gender: str
    occupation: str
    backstory: str


class AgentProfile(BaseModel):
    """The complete definition of an Agent's soul."""

    identity: Identity
    psychology: Psychology
    morality: MoralCompass
    emotions: EmotionalProfile
    cognition: Cognition
    communication: CommunicationStyle
