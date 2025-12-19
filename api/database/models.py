from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
from typing import Any


class WorldModel(Base):
    __tablename__ = "worlds"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agents = relationship(
        "AgentModel", back_populates="world", cascade="all, delete-orphan"
    )


class AgentModel(Base):
    __tablename__ = "agents"

    id: int = Column(Integer, primary_key=True, index=True)
    world_id: int = Column(Integer, ForeignKey("worlds.id"))
    name: str = Column(String, index=True)

    profile_json: Any = Column(JSON)

    short_term_memory: Any = Column(JSON, default=list)
    mid_term_memory: Any = Column(JSON, default=list)
    current_situation: str = Column(String, default="")

    world = relationship("WorldModel", back_populates="agents")
