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
    """
    # Deserialize the profile JSON back into Pydantic
    profile = AgentProfile.model_validate(agent_db.profile_json)

    # Create COPIES of the lists.
    stm = list(agent_db.short_term_memory) if agent_db.short_term_memory else []
    mtm = list(agent_db.mid_term_memory) if agent_db.mid_term_memory else []

    situation = str(agent_db.current_situation) if agent_db.current_situation else ""

    agent = Agent(
        profile=profile,
        memory_store=memory_store,
        initial_short_term_memory=stm,
        initial_mid_term_memory=mtm,
        situation=situation,
    )

    agent.archival_memory = list(stm)

    return agent
