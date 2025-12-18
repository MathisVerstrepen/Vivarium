from rich.console import Console
from rich.panel import Panel
from schemas.personnality import (
    AgentProfile,
    Identity,
    Psychology,
    MoralCompass,
    EmotionalProfile,
    Cognition,
    CommunicationStyle,
)
from services.agent import Agent
from services.memory_store import MemoryStore
from helpers.printers import print_memory_state

console = Console()

MAX_CONVERSATION_TURNS = 100
MEMORY_LENGTH_THRESHOLD = 16
MEMORY_COMPRESSION_BATCH = 8


def create_profiles():
    # 1. SOPHIE: Creative, enthusiastic, spontaneous artist
    sophie = AgentProfile(
        identity=Identity(
            name="Sophie",
            age=21,
            gender="Female",
            occupation="Art Student",
            backstory="Lives for creativity and new experiences. Loves meeting new people and sharing ideas.",
        ),
        psychology=Psychology(
            openness=0.95,
            conscientiousness=0.4,
            extraversion=0.85,
            agreeableness=0.75,
            neuroticism=0.4,
        ),
        morality=MoralCompass(
            care_harm=0.8,
            fairness_cheating=0.7,
            loyalty_betrayal=0.6,
            authority_subversion=0.7,
            sanctity_degradation=0.3,
        ),
        emotions=EmotionalProfile(
            base_mood="Excited and curious",
            emotional_volatility=0.6,
            attachment_style="Secure",
            triggers=["Boredom", "Rigid rules"],
        ),
        cognition=Cognition(
            decision_basis="Intuition",
            impulsivity=0.8,
        ),
        communication=CommunicationStyle(
            verbosity=0.8,
            formality=0.2,
            tone="Warm, playful, expressive",
        ),
    )

    # 2. MARCUS: Calm, thoughtful, grounded engineer
    marcus = AgentProfile(
        identity=Identity(
            name="Marcus",
            age=24,
            gender="Male",
            occupation="Software Engineer Student",
            backstory="Enjoys solving problems and learning how things work. Appreciates people who bring energy to his life.",
        ),
        psychology=Psychology(
            openness=0.7,
            conscientiousness=0.85,
            extraversion=0.5,
            agreeableness=0.7,
            neuroticism=0.25,
        ),
        morality=MoralCompass(
            care_harm=0.7,
            fairness_cheating=0.85,
            loyalty_betrayal=0.8,
            authority_subversion=0.4,
            sanctity_degradation=0.3,
        ),
        emotions=EmotionalProfile(
            base_mood="Calm and content",
            emotional_volatility=0.2,
            attachment_style="Secure",
            triggers=["Dishonesty", "Chaos without purpose"],
        ),
        cognition=Cognition(
            decision_basis="Logic",
            impulsivity=0.2,
        ),
        communication=CommunicationStyle(
            verbosity=0.5,
            formality=0.5,
            tone="Steady, curious, supportive",
        ),
    )

    return sophie, marcus


def main():
    memory_store = MemoryStore()

    p1, p2 = create_profiles()

    agent_a = Agent(
        p1,
        memory_store=memory_store,
        memory_trigger=MEMORY_LENGTH_THRESHOLD,
        memory_batch_size=MEMORY_COMPRESSION_BATCH,
    )
    agent_b = Agent(
        p2,
        memory_store=memory_store,
        memory_trigger=MEMORY_LENGTH_THRESHOLD,
        memory_batch_size=MEMORY_COMPRESSION_BATCH,
    )

    console.print(
        Panel.fit(
            f"Start: {p1.identity.name} vs {p2.identity.name}", style="bold green"
        )
    )
    console.print(
        f"[dim]Memory Config: Trigger={MEMORY_LENGTH_THRESHOLD}, Batch={MEMORY_COMPRESSION_BATCH}[/dim]\n"
    )

    seed = "You are meeting for the first time at a student party."
    agent_a.situation = seed
    agent_b.situation = seed

    conversation_active = True
    turn_count = 0

    while conversation_active and turn_count < MAX_CONVERSATION_TURNS:
        current_speaker = agent_a if turn_count % 2 == 0 else agent_b
        other_agent = agent_b if current_speaker == agent_a else agent_a

        # Check buffer size BEFORE act to see if compression is about to happen
        pre_act_size = len(current_speaker.short_term_memory)

        # ACT
        action = current_speaker.act(other_agent.profile.identity.name)

        # Check buffer size AFTER act to detect change
        post_act_size = len(current_speaker.short_term_memory)

        # VISUALIZE
        color = "cyan" if current_speaker == agent_a else "yellow"
        console.print(
            f"[{color} bold]{current_speaker.profile.identity.name}[/{color} bold] ({action.mood})"
        )
        console.print(f"[italic dim]Thought: {action.inner_monologue}[/italic dim]")
        console.print(f'Says: "{action.speech}"\n')

        # Log Memory State
        if (
            pre_act_size >= MEMORY_LENGTH_THRESHOLD
            and post_act_size < MEMORY_LENGTH_THRESHOLD
        ):
            console.print(
                f"[bold red] >>> MEMORY COMPRESSED! {pre_act_size} items -> {post_act_size} items. Added to Mid-Term.[/bold red]"
            )
        else:
            console.print(
                f"[dim]Memory Buffer: {post_act_size}/{MEMORY_LENGTH_THRESHOLD}[/dim]"
            )

        # LISTEN
        other_agent.listen(action.speech, current_speaker.profile.identity.name)

        if action.end_conversation:
            conversation_active = False

        turn_count += 1
        print("-" * 20)

    console.print(
        "[bold magenta]End of Conversation. Extracting Memories to Vector DB...[/bold magenta]"
    )

    agent_a.process_conversation_end()
    agent_b.process_conversation_end()

    # Print final memory states
    print_memory_state(agent_a, "mid_term")
    print_memory_state(agent_b, "mid_term")

    # Verification: Check what Sophie remembers about Marcus
    console.print(
        "\n[bold blue]Verification: What does Sophie remember about Marcus?[/bold blue]"
    )
    mems = memory_store.retrieve_relevant_memories("Sophie", "Marcus", limit=10)
    for m in mems:
        console.print(f"- {m}")

    agent_a.clear_memory()
    agent_b.clear_memory()


if __name__ == "__main__":
    main()
