from schemas.interaction import AgentOutput
from schemas.personnality import AgentProfile
from helpers.openrouter import run_llm_with_schema


class Agent:
    def __init__(
        self, profile: AgentProfile, model: str = "google/gemini-3-flash-preview"
    ):
        self.profile = profile
        self.model = model
        self.memory: list[str] = []  # Simple list for PoC, will be Vector DB later

    def _build_system_prompt(self, other_agent_name: str) -> str:
        """Constructs the 'Soul' of the agent for the LLM."""
        p = self.profile
        psy = p.psychology

        return f"""
        You are roleplaying as {p.identity.name}. Your answer should reflect your unique identity and psychology. Think carefully before you respond.
        Keep your answers concise and in character.
        
        # YOUR PROFILE
        Age: {p.identity.age}
        Job: {p.identity.occupation}
        Backstory: {p.identity.backstory}
        Speaking Style: {p.identity.speaking_style}
        
        # YOUR PSYCHOLOGY (0.0 Low - 1.0 High)
        - Openness: {psy.openness}
        - Conscientiousness: {psy.conscientiousness}
        - Extraversion: {psy.extraversion}
        - Agreeableness: {psy.agreeableness}
        - Neuroticism: {psy.neuroticism}
        
        # CONTEXT
        You are currently in a room talking to [{other_agent_name}].
        
        # INSTRUCTIONS
        1. Read the conversation history.
        2. Form an internal thought based on your personality.
        3. Decide on your mood.
        4. distinct from your thoughts, generate your speech.
        """

    def listen(self, message: str, sender_name: str):
        """Adds a message to short-term memory."""
        self.memory.append(f"{sender_name}: {message}")

    def act(self, other_agent_name: str) -> AgentOutput:
        """Decides on a response based on memory and personality."""

        # Format memory for the prompt
        conversation_history = "\n".join(self.memory[-10:])  # Keep last 10 interactions
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

        # Add own speech to memory so we remember what we said
        self.memory.append(f"{self.profile.identity.name}: {response.speech}")

        return response
