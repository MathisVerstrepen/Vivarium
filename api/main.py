from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, cast

# Database & CRUD
from database.database import get_db, engine, Base
from database import crud

# Schemas
from schemas.personnality import AgentProfile
from schemas.api_dtos import (
    CreateWorldRequest,
    WorldResponse,
    CreateAgentRequest,
    AgentResponse,
    InteractRequest,
    InteractionResponse,
    WhisperRequest,
    AgentStateResponse,
    ChatRequest,
    ChatResponse,
    EndChatRequest,
    EndChatResponse,
)

# Services
from services.memory_store import MemoryStore
from services.factory import hydrate_agent_service

GOD_PLAYER_NAME = "Mathis"

# Initialize Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vivarium API", description="AI Playground Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Vector Store
memory_store = MemoryStore()

# --- ROUTES ---


@app.get("/")
async def health_check():
    return {"status": "ok", "db": "sqlite"}


# 1. WORLD MANAGEMENT


@app.post("/worlds", response_model=WorldResponse)
async def create_world(req: CreateWorldRequest, db: Session = Depends(get_db)):
    db_world = crud.create_world(db, req.name)
    return WorldResponse(id=db_world.id, name=db_world.name)


@app.get("/worlds", response_model=List[WorldResponse])
async def list_worlds(db: Session = Depends(get_db)):
    worlds = crud.get_worlds(db)
    return [WorldResponse(id=w.id, name=w.name) for w in worlds]


# 2. AGENT MANAGEMENT


@app.post("/agents", response_model=AgentResponse)
async def create_agent(req: CreateAgentRequest, db: Session = Depends(get_db)):
    # Validate World
    world = crud.get_world_by_id(db, req.world_id)
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    # Create Agent
    db_agent = crud.create_agent(
        db,
        world_id=req.world_id,
        profile=req.profile,
        initial_situation=req.initial_situation or "",
        x=req.x if req.x is not None else 400.0,
        y=req.y if req.y is not None else 300.0,
    )

    return AgentResponse(
        id=db_agent.id,
        world_id=db_agent.world_id,
        name=db_agent.name,
        current_situation=db_agent.current_situation,
        x=db_agent.x,
        y=db_agent.y,
    )


@app.get("/worlds/{world_id}/agents", response_model=List[AgentResponse])
async def list_agents_in_world(world_id: int, db: Session = Depends(get_db)):
    agents = crud.get_agents_by_world(db, world_id)
    return [
        AgentResponse(
            id=a.id,
            world_id=a.world_id,
            name=a.name,
            current_situation=a.current_situation,
            x=a.x,
            y=a.y,
        )
        for a in agents
    ]


@app.get("/agents/{agent_id}", response_model=AgentStateResponse)
async def get_agent_detail(agent_id: int, db: Session = Depends(get_db)):
    agent_db = crud.get_agent(db, agent_id)
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    profile = AgentProfile.model_validate(agent_db.profile_json)

    # Casts for response model
    stm = cast(List[str], agent_db.short_term_memory)
    mtm = cast(List[str], agent_db.mid_term_memory)

    return AgentStateResponse(
        id=agent_db.id,
        name=agent_db.name,
        profile=profile,
        short_term_memory=stm,
        mid_term_memory=mtm,
        current_situation=agent_db.current_situation,
        x=agent_db.x,
        y=agent_db.y,
    )


@app.put("/agents/{agent_id}", response_model=AgentStateResponse)
async def update_agent(
    agent_id: int, profile: AgentProfile, db: Session = Depends(get_db)
):
    updated_agent = crud.update_agent_profile(db, agent_id, profile)
    if not updated_agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    stm = cast(List[str], updated_agent.short_term_memory)
    mtm = cast(List[str], updated_agent.mid_term_memory)

    return AgentStateResponse(
        id=updated_agent.id,
        name=updated_agent.name,
        profile=AgentProfile.model_validate(updated_agent.profile_json),
        short_term_memory=stm,
        mid_term_memory=mtm,
        current_situation=updated_agent.current_situation,
        x=updated_agent.x,
        y=updated_agent.y,
    )


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    success = crud.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "success", "id": agent_id}


# 3. INTERACTION LOOP


@app.post("/interact", response_model=InteractionResponse)
async def interact(req: InteractRequest, db: Session = Depends(get_db)):
    # 1. Fetch Data
    source_db = crud.get_agent(db, req.source_agent_id)
    target_db = crud.get_agent(db, req.target_agent_id)

    if not source_db or not target_db:
        raise HTTPException(status_code=404, detail="One or more agents not found")

    if source_db.world_id != target_db.world_id:
        raise HTTPException(status_code=400, detail="Agents are in different worlds!")

    # 2. Hydrate Logic Services
    source_agent = hydrate_agent_service(memory_store, source_db)
    target_agent = hydrate_agent_service(memory_store, target_db)

    pre_act_count = len(source_agent.short_term_memory)

    # 3. Execute AI Logic
    output = source_agent.act(target_agent.profile.identity.name)
    target_agent.listen(output.speech, source_agent.profile.identity.name)

    # 4. Persist Changes via CRUD
    # Update Source (Handling potential memory compression)
    crud.update_agent_memory(
        db,
        agent_id=source_db.id,
        short_term_mem=source_agent.short_term_memory,
        mid_term_mem=source_agent.mid_term_memory,
    )

    # Update Target (Added new message)
    crud.update_agent_memory(
        db,
        agent_id=target_db.id,
        short_term_mem=target_agent.short_term_memory,
        # Target doesn't compress memory when listening, so we don't need to update mid_term
    )

    was_compressed = len(source_agent.short_term_memory) < pre_act_count

    return InteractionResponse(
        source_agent_id=source_db.id,
        target_agent_id=target_db.id,
        source_agent_name=source_db.name,
        output=output,
        memory_compressed=was_compressed,
    )


@app.post("/agent/whisper")
async def whisper(req: WhisperRequest, db: Session = Depends(get_db)):
    agent_db = crud.get_agent(db, req.agent_id)
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    crud.append_agent_short_term_memory(
        db, agent_id=req.agent_id, message=f"[Internal Subconscious]: {req.content}"
    )

    return {"status": "success"}


@app.post("/agent/chat", response_model=ChatResponse)
async def chat_with_agent(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Direct Player -> Agent interaction.
    """
    agent_db = crud.get_agent(db, req.agent_id)
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 1. Hydrate
    agent_service = hydrate_agent_service(memory_store, agent_db)

    # 2. Update Service State
    agent_service.listen(req.message, GOD_PLAYER_NAME)
    output = agent_service.act(GOD_PLAYER_NAME)

    # 3. Save
    crud.update_agent_memory(
        db,
        agent_id=agent_db.id,
        short_term_mem=agent_service.short_term_memory,
        mid_term_mem=agent_service.mid_term_memory,
    )

    return ChatResponse(agent_id=agent_db.id, agent_name=agent_db.name, response=output)


@app.post("/agent/chat/end", response_model=EndChatResponse)
async def end_chat_session(req: EndChatRequest, db: Session = Depends(get_db)):
    """
    Ends the conversation.
    1. Triggers Long-Term Memory extraction (summarizing the chat into facts).
    2. Saves facts to Vector DB.
    3. Clears Short-Term Memory in SQL DB.
    """
    agent_db = crud.get_agent(db, req.agent_id)
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 1. Hydrate Service
    agent_service = hydrate_agent_service(memory_store, agent_db)

    # 2. Extract Memories
    memories_created = agent_service.process_conversation_end(
        other_agent_name=GOD_PLAYER_NAME
    )

    # 3. Clear Internal Service State
    agent_service.clear_memory()

    # 4. Update SQL Database
    crud.update_agent_memory(
        db,
        agent_id=agent_db.id,
        short_term_mem=[],
        mid_term_mem=agent_service.mid_term_memory,
    )

    return EndChatResponse(agent_id=agent_db.id, memories_created=memories_created)
