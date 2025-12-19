from sqlalchemy.orm import Session
from typing import List, Optional

from database.models import WorldModel, AgentModel
from schemas.personnality import AgentProfile

# --- WORLD OPERATIONS ---


def create_world(db: Session, name: str) -> WorldModel:
    db_world = WorldModel(name=name)
    db.add(db_world)
    db.commit()
    db.refresh(db_world)
    return db_world


def get_worlds(db: Session) -> List[WorldModel]:
    return db.query(WorldModel).all()


def get_world_by_id(db: Session, world_id: int) -> Optional[WorldModel]:
    return db.query(WorldModel).filter(WorldModel.id == world_id).first()


# --- AGENT OPERATIONS ---


def create_agent(
    db: Session, world_id: int, profile: AgentProfile, initial_situation: str
) -> AgentModel:
    """
    Creates a new agent. Serializes the Pydantic profile into JSON.
    """
    db_agent = AgentModel(
        world_id=world_id,
        name=profile.identity.name,
        profile_json=profile.model_dump(),  # Serialize Pydantic to JSON
        current_situation=initial_situation,
        short_term_memory=[],
        mid_term_memory=[],
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def get_agent(db: Session, agent_id: int) -> Optional[AgentModel]:
    return db.query(AgentModel).filter(AgentModel.id == agent_id).first()


def get_agents_by_world(db: Session, world_id: int) -> List[AgentModel]:
    return db.query(AgentModel).filter(AgentModel.world_id == world_id).all()


def update_agent_memory(
    db: Session,
    agent_id: int,
    short_term_mem: List[str],
    mid_term_mem: Optional[List[str]] = None,
):
    """
    Updates the memory state of an agent.
    """
    agent = get_agent(db, agent_id)
    if agent:
        agent.short_term_memory = short_term_mem
        if mid_term_mem is not None:
            agent.mid_term_memory = mid_term_mem

        db.commit()
        db.refresh(agent)
    return agent


def append_agent_short_term_memory(db: Session, agent_id: int, message: str):
    """
    Appends a single message to STM (useful for Whispers).
    """
    agent = get_agent(db, agent_id)
    if agent:
        current_mem = list(agent.short_term_memory)
        current_mem.append(message)
        agent.short_term_memory = current_mem
        db.commit()
