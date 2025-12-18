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

console = Console()


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
    p1, p2 = create_profiles()
    agent_a = Agent(p1)
    agent_b = Agent(p2)

    console.print(
        Panel.fit(
            f"Start: {p1.identity.name} vs {p2.identity.name}", style="bold green"
        )
    )

    seed_topic = "They meet at a student party"
    agent_a.memory.append(f"SYSTEM: {seed_topic}")
    agent_b.memory.append(f"SYSTEM: {seed_topic}")

    console.print(f"[italic grey]{seed_topic}[/italic grey]\n")

    turns = 100
    current_speaker = agent_a
    other_agent = agent_b

    for _ in range(turns):
        action = current_speaker.act(other_agent.profile.identity.name)

        color = "cyan" if current_speaker == agent_a else "yellow"
        console.print(
            f"[{color} bold]{current_speaker.profile.identity.name}[/{color} bold] ({action.mood})"
        )
        console.print(f"[italic dim]Thought: {action.inner_monologue}[/italic dim]")
        console.print(f'Says: "{action.speech}"\n')

        if action.end_conversation:
            console.print(Panel.fit("Conversation ended.", style="bold red"))
            break

        other_agent.listen(action.speech, current_speaker.profile.identity.name)
        current_speaker, other_agent = other_agent, current_speaker


if __name__ == "__main__":
    main()
