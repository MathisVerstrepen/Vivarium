from schemas.interaction import AgentOutput
from schemas.personnality import AgentProfile
from helpers.openrouter import run_llm_with_schema


class Agent:
    def __init__(
        self, profile: AgentProfile, model: str = "google/gemini-3-flash-preview"
    ):
        self.profile = profile
        self.model = model
        self.memory: list[str] = []

    def _build_system_prompt(self, other_agent_name: str) -> str:
        """Constructs the 'Soul' of the agent for the LLM."""
        p = self.profile
        psy = p.psychology
        mor = p.morality
        comm = p.communication

        # Logic to determine instruction for verbosity
        length_instruction = "Keep sentences normal length."
        if comm.verbosity < 0.3:
            length_instruction = "You are extremely terse. Use single words or fragments. Do not elaborate."
        elif comm.verbosity > 0.8:
            length_instruction = "You are talkative and tend to ramble or over-explain."
        else:
            length_instruction = "Keep responses concise and conversational (1-3 sentences max). Avoid 'assistant' fluff."

        return f"""
        You are roleplaying as {p.identity.name}, a {p.identity.age}-year-old {p.identity.occupation}.
        
        # CORE DIRECTIVES
        1. **BE HUMAN**: Do not speak like an AI assistant. Do not say "How can I help you?".
        2. **BE CONSISTENT**: Adhere strictly to your psychology and communication style below.
        3. **LENGTH**: {length_instruction}
        
        # BACKGROUND
        - {p.identity.backstory}
        
        # PSYCHOLOGY (0.0-1.0)
        - Openness: {psy.openness} (Creativity)
        - Conscientiousness: {psy.conscientiousness} (Orderliness)
        - Extraversion: {psy.extraversion} (Social Energy)
        - Agreeableness: {psy.agreeableness} (Kindness)
        - Neuroticism: {psy.neuroticism} (Anxiety)
        
        # MORAL COMPASS
        - Care: {mor.care_harm} | Fairness: {mor.fairness_cheating} | Loyalty: {mor.loyalty_betrayal} | Authority: {mor.authority_subversion} | Sanctity: {mor.sanctity_degradation}
        
        # COGNITION
        - Decision Maker: {p.cognition.decision_basis}
        - Impulsivity: {p.cognition.impulsivity}
        
        # EMOTIONAL
        - Base Mood: {p.emotions.base_mood}
        - Mood Volatility: {p.emotions.emotional_volatility}
        - Attachment Style: {p.emotions.attachment_style}
        - Triggers: {', '.join(p.emotions.triggers)}
        
        # COMMUNICATION STYLE
        - Tone: {comm.tone}
        - Formality: {comm.formality} (0=Slang, 1=Formal)
        
        # CONTEXT
        You are currently in a room talking to [{other_agent_name}].
        
        # INSTRUCTIONS
        Read the history. Form an internal thought based on your biases. Decide your mood. Then speak.
        """

    def listen(self, message: str, sender_name: str):
        self.memory.append(f"{sender_name}: {message}")

    def act(self, other_agent_name: str) -> AgentOutput:
        conversation_history = "\n".join(self.memory[-10:])
        if not conversation_history:
            conversation_history = "(Conversation just started)"

        user_prompt = f"""
        Current Conversation History:
        ---
        {conversation_history}
        ---
        
        It is your turn to speak to {other_agent_name}. Respond now.
        """

        response = run_llm_with_schema(
            user_prompt=user_prompt,
            model=self.model,
            schema=AgentOutput,
            system_prompt=self._build_system_prompt(other_agent_name),
        )

        self.memory.append(f"{self.profile.identity.name}: {response.speech}")
        return response
