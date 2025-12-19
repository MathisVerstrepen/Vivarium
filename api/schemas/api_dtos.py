from pydantic import BaseModel
from typing import List, Optional
from schemas.interaction import AgentOutput
from schemas.personnality import AgentProfile


# --- WORLD DTOs ---
class CreateWorldRequest(BaseModel):
    name: str


class WorldResponse(BaseModel):
    id: int
    name: str


# --- AGENT DTOs ---
class CreateAgentRequest(BaseModel):
    world_id: int
    profile: AgentProfile
    initial_situation: Optional[str] = "You are standing in the world."


class AgentResponse(BaseModel):
    id: int
    world_id: int
    name: str
    current_situation: str


# --- INTERACTION DTOs ---
class InteractRequest(BaseModel):
    source_agent_id: int
    target_agent_id: int


class InteractionResponse(BaseModel):
    source_agent_id: int
    target_agent_id: int
    source_agent_name: str
    output: AgentOutput
    memory_compressed: bool


class WhisperRequest(BaseModel):
    agent_id: int
    content: str


class AgentStateResponse(BaseModel):
    id: int
    profile: AgentProfile
    short_term_memory: List[str]
    mid_term_memory: List[str]
    current_situation: str
