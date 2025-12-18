from typing import List
from schemas.interaction import AgentOutput
from schemas.personnality import AgentProfile
from schemas.memory import MemoryExtraction
from helpers.openrouter import run_llm, run_llm_with_schema
from const.prompts import (
    LONG_TERM_MEMORY_EXTRACTION_PROMPT,
    MID_TERM_MEMORY_SUMMARY_PROMPT,
    AGENT_SYSTEM_PROMPT,
)


class Agent:
    def __init__(
        self,
        profile: AgentProfile,
        model: str = "google/gemini-3-flash-preview",
        memory_trigger: int = 15,
        memory_batch_size: int = 5,
    ):
        self.profile = profile
        self.model = model

        # Configuration for the Sliding Window
        self.MEMORY_TRIGGER = memory_trigger
        self.MEMORY_BATCH_SIZE = memory_batch_size

        # 1. Short Term: Raw strings (The active conversation window for the LLM context)
        self.short_term_memory: List[str] = []

        # 2. Mid Term: Summarized blocks (The narrative history for the LLM context)
        self.mid_term_memory: List[str] = []

        # 3. Archival Memory: The complete, raw history of the current conversation session.
        self.archival_memory: List[str] = []

        # 4. Long Term: Persistent facts (The "Vault")
        self.long_term_memory: List[str] = []

    def _build_system_prompt(self, other_agent_name: str) -> str:
        """Constructs the 'Soul' of the agent for the LLM."""
        p = self.profile
        psy = p.psychology
        mor = p.morality
        comm = p.communication

        # Format Long Term Memory
        ltm_context = "No previous knowledge."
        if self.long_term_memory:
            ltm_context = "\n- ".join(self.long_term_memory)

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

    def process_conversation_end(self):
        """Finalizes the conversation by extracting long-term insights."""
        # We use archival_memory here to ensure no details are lost due to summarization
        full_context = "\n".join(self.archival_memory)

        extraction = run_llm_with_schema(
            user_prompt=LONG_TERM_MEMORY_EXTRACTION_PROMPT.format(
                agent_name=self.profile.identity.name,
                conversation_text=full_context,
            ),
            model=self.model,
            schema=MemoryExtraction,
        )

        # Commit to the Vault
        self.long_term_memory.extend(extraction.facts)

        return extraction

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
        # If we are at 15 messages, this brings us down to 10 before generating the new response.
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

        response = run_llm_with_schema(
            user_prompt=user_prompt,
            model=self.model,
            schema=AgentOutput,
            system_prompt=self._build_system_prompt(other_agent_name),
        )

        self.listen(response.speech, self.profile.identity.name)

        return response
