from typing import List, Optional
from schemas.interaction import AgentOutput
from schemas.personnality import AgentProfile
from schemas.memory import MemoryExtraction, NewMemory, MergedMemory
from helpers.openrouter import run_llm, run_llm_with_schema
from services.memory_store import MemoryStore
from const.prompts import (
    LONG_TERM_MEMORY_EXTRACTION_PROMPT,
    MID_TERM_MEMORY_SUMMARY_PROMPT,
    AGENT_SYSTEM_PROMPT,
    MEMORY_MERGE_PROMPT,
)


class Agent:
    def __init__(
        self,
        profile: AgentProfile,
        memory_store: MemoryStore,
        model: str = "google/gemini-3-flash-preview",
        memory_trigger: int = 15,
        memory_batch_size: int = 5,
        initial_short_term_memory: Optional[List[str]] = None,
        initial_mid_term_memory: Optional[List[str]] = None,
        situation: str = "",
    ):
        self.profile = profile
        self.model = model
        self.memory_store = memory_store

        # Configuration for the Sliding Window
        self.MEMORY_TRIGGER = memory_trigger
        self.MEMORY_BATCH_SIZE = memory_batch_size

        # Context
        self.situation = situation

        # 1. Short Term: Raw strings (The active conversation window)
        self.short_term_memory: List[str] = (
            initial_short_term_memory if initial_short_term_memory else []
        )

        # 2. Mid Term: Summarized blocks (The narrative history)
        self.mid_term_memory: List[str] = (
            initial_mid_term_memory if initial_mid_term_memory else []
        )

        # 3. Archival Memory: For this session (not persisted in SQL currently, usually transient)
        self.archival_memory: List[str] = []

    def _build_system_prompt(self, other_agent_name: str) -> str:
        """Constructs the 'Soul' of the agent for the LLM."""
        p = self.profile
        psy = p.psychology
        mor = p.morality
        comm = p.communication

        # --- VECTOR RETRIEVAL LOGIC ---
        query_context = ""
        if len(self.short_term_memory) > 0:
            query_context = "\n".join(self.short_term_memory[-3:])
        else:
            query_context = f"Who is {other_agent_name}? {self.situation}"

        retrieved_memories = self.memory_store.retrieve_relevant_memories(
            agent_name=self.profile.identity.name, query_text=query_context, limit=5
        )

        ltm_context = "No relevant memories found."
        if retrieved_memories:
            ltm_context = "\n- ".join(retrieved_memories)
        print(f"[DEBUG] Retrieved LTM for {p.identity.name}:\n- {ltm_context}\n")

        # Logic to determine instruction for verbosity
        length_instruction = "Keep sentences normal length."
        if comm.verbosity < 0.3:
            length_instruction = "You are extremely terse. Use single words or fragments. Do not elaborate."
        elif comm.verbosity > 0.8:
            length_instruction = "You are talkative and tend to ramble or over-explain."
        else:
            length_instruction = "Keep responses concise and conversational (1-3 sentences max). Avoid 'assistant' fluff."

        return AGENT_SYSTEM_PROMPT.format(
            identity_name=p.identity.name,
            identity_age=p.identity.age,
            identity_occupation=p.identity.occupation,
            length_instruction=length_instruction,
            ltm_context=ltm_context,
            identity_backstory=p.identity.backstory,
            psy_openness=psy.openness,
            psy_conscientiousness=psy.conscientiousness,
            psy_extraversion=psy.extraversion,
            psy_agreeableness=psy.agreeableness,
            psy_neuroticism=psy.neuroticism,
            mor_care_harm=mor.care_harm,
            mor_fairness_cheating=mor.fairness_cheating,
            mor_loyalty_betrayal=mor.loyalty_betrayal,
            mor_authority_subversion=mor.authority_subversion,
            mor_sanctity_degradation=mor.sanctity_degradation,
            cognition_decision_basis=p.cognition.decision_basis,
            cognition_impulsivity=p.cognition.impulsivity,
            emotions_base_mood=p.emotions.base_mood,
            emotions_emotional_volatility=p.emotions.emotional_volatility,
            emotions_attachment_style=p.emotions.attachment_style,
            emotions_triggers=", ".join(p.emotions.triggers),
            comm_tone=comm.tone,
            comm_formality=comm.formality,
            situation=self.situation,
            other_agents_names=other_agent_name,
        )

    def _compress_memory(self):
        """
        Sliding Window Logic:
        If ShortTerm >= 15, cut the oldest 5, summarize them, and store in MidTerm.
        ShortTerm becomes 10.
        """
        if len(self.short_term_memory) >= self.MEMORY_TRIGGER:
            # 1. Identify the chunk to compress (The oldest 'batch_size' messages)
            chunk_to_compress = self.short_term_memory[: self.MEMORY_BATCH_SIZE]

            # 2. IMMEDIATE SLICING: Remove them from short term memory
            self.short_term_memory = self.short_term_memory[self.MEMORY_BATCH_SIZE :]

            # 3. Generate Summary
            conversation_text = "\n".join(chunk_to_compress)
            prompt = MID_TERM_MEMORY_SUMMARY_PROMPT.format(
                agent_name=self.profile.identity.name,
                conversation_text=conversation_text,
            )

            summary = run_llm(prompt, self.model)

            # 4. Store in Mid Term
            self.mid_term_memory.append(f"{summary}")

    def process_conversation_end(self, other_agent_name: str) -> List[str]:
        """
        Finalizes the conversation:
        1. Extracts categorized memories.
        2. Checks for duplicates in the Vector DB.
        3. Merges or Inserts.
        """
        full_context = "\n".join(self.archival_memory)

        # 1. Extraction
        extraction = run_llm_with_schema(
            user_prompt=LONG_TERM_MEMORY_EXTRACTION_PROMPT.format(
                agent_name=self.profile.identity.name,
                other_agent_name=other_agent_name,
                conversation_text=full_context,
            ),
            model=self.model,
            schema=MemoryExtraction,
        )

        final_facts_added = []

        # 2. Deduplication & Storage Loop
        for mem in extraction.memories:
            # Search for similar memory
            nearest = self.memory_store.retrieve_nearest_memory(
                agent_name=self.profile.identity.name,
                query_text=mem.content,
                threshold_distance=0.45,  # Strict threshold for "Is this the same fact?"
            )

            if nearest:
                print(
                    f"[Memory] Found duplicate/conflict for '{mem.content}' -> '{nearest['text']}'"
                )

                # Ask LLM to merge
                merge_result = run_llm_with_schema(
                    user_prompt=MEMORY_MERGE_PROMPT.format(
                        existing_memory=nearest["text"], new_memory=mem.content
                    ),
                    model=self.model,
                    schema=MergedMemory,
                )

                # Delete old memory
                self.memory_store.delete_memory(nearest["id"])

                # Insert merged result(s)
                for fact in merge_result.facts:
                    new_mem_obj = NewMemory(
                        category=mem.category, subject=mem.subject, content=fact
                    )
                    self.memory_store.add_memory(
                        self.profile.identity.name, new_mem_obj
                    )
                    final_facts_added.append(fact)

            else:
                # No duplicate found, just add
                self.memory_store.add_memory(self.profile.identity.name, mem)
                final_facts_added.append(mem.content)

        return final_facts_added

    def clear_memory(self):
        """Resets the temporary memories for the next session."""
        self.short_term_memory = []
        self.mid_term_memory = []
        self.archival_memory = []

    def listen(self, message: str, sender_name: str):
        formatted_message = f"{sender_name}: {message}"
        self.short_term_memory.append(formatted_message)
        self.archival_memory.append(formatted_message)

    def act(self, other_agent_name: str) -> AgentOutput:
        # 1. Check Memory Pressure BEFORE acting
        self._compress_memory()

        # 2. Construct Context
        # Mid-Term (Summaries) + Short-Term (Recent Verbatim)
        context_str = "\n".join(self.mid_term_memory + self.short_term_memory)
        if not context_str:
            context_str = "(Conversation just started)"

        user_prompt = f"""
        Current Conversation History:
        ---
        {context_str}
        ---
        
        It is your turn to speak to {other_agent_name}. Respond now.
        """

        print(f"[DEBUG] Acting with prompt:\n{user_prompt}\n")

        response = run_llm_with_schema(
            user_prompt=user_prompt,
            model=self.model,
            schema=AgentOutput,
            system_prompt=self._build_system_prompt(other_agent_name),
        )

        self.listen(response.speech, self.profile.identity.name)

        return response
