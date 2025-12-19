from typing import List, cast

# Database & CRUD
from database.models import AgentModel

# Schemas
from schemas.personnality import AgentProfile

# Services
from services.agent import Agent
from services.memory_store import MemoryStore

def hydrate_agent_service(memory_store: MemoryStore, agent_db: AgentModel) -> Agent:
    """
    Factory function: Converts a Database Model into a Functional Agent Service.
    We use explicit casting here to satisfy type checkers regarding JSON columns.
    """
    # Deserialize the profile JSON back into Pydantic
    profile = AgentProfile.model_validate(agent_db.profile_json)

    # Explicitly cast JSON columns to their expected Python types
    stm = cast(List[str], agent_db.short_term_memory)
    mtm = cast(List[str], agent_db.mid_term_memory)
    situation = cast(str, agent_db.current_situation)

    return Agent(
        profile=profile,
        memory_store=memory_store,
        initial_short_term_memory=stm,
        initial_mid_term_memory=mtm,
        situation=situation,
    )
