from rich.console import Console
from rich.panel import Panel
from schemas.personnality import AgentProfile, Identity, Psychology
from services.agent import Agent

console = Console()


def create_profiles():
    """Factory function to create two distinct personalities."""

    emma = AgentProfile(
        identity=Identity(
            name="Emma",
            age=20,
            occupation="Psychology Student",
            backstory="She is passionate about understanding human behavior and loves reading.",
            speaking_style="Thoughtful, curious, often asks questions.",
        ),
        psychology=Psychology(
            openness=0.8,
            conscientiousness=0.6,
            extraversion=0.5,
            agreeableness=0.7,
            neuroticism=0.6,
        ),
    )

    lucas = AgentProfile(
        identity=Identity(
            name="Lucas",
            age=21,
            occupation="Business Student",
            backstory="He dreams of starting his own tech company and loves networking.",
            speaking_style="Confident, persuasive, sometimes competitive.",
        ),
        psychology=Psychology(
            openness=0.6,
            conscientiousness=0.7,
            extraversion=0.85,
            agreeableness=0.5,
            neuroticism=0.3,
        ),
    )

    return emma, lucas


def main():
    # 1. Setup
    p1, p2 = create_profiles()
    agent_a = Agent(p1)
    agent_b = Agent(p2)

    console.print(
        Panel.fit(
            f"Simulation Start: {p1.identity.name} vs {p2.identity.name}",
            style="bold green",
        )
    )

    # 2. Seed the conversation
    seed_topic = (
        "Casual chat. They are meeting for the first time at a university event."
    )
    agent_a.memory.append(f"SYSTEM: {seed_topic}")
    agent_b.memory.append(f"SYSTEM: {seed_topic}")

    console.print(f"[italic grey]{seed_topic}[/italic grey]\n")

    # 3. Simulation Loop
    turns = 100
    current_speaker = agent_b
    other_agent = agent_a

    for _ in range(turns):
        # A. The Agent Thinks and Speaks
        action = current_speaker.act(other_agent.profile.identity.name)

        # B. Display the output
        color = "cyan" if current_speaker == agent_a else "yellow"

        console.print(
            f"[{color} bold]{current_speaker.profile.identity.name}[/{color} bold] ({action.mood})"
        )
        console.print(f"[italic dim]Thought: {action.inner_monologue}[/italic dim]")
        console.print(f'Says: "{action.speech}"\n')

        if action.end_conversation:
            console.print(
                Panel.fit(
                    f"Conversation ended by {current_speaker.profile.identity.name}.",
                    style="bold red",
                )
            )
            break

        # C. The Other Agent Hears it
        other_agent.listen(action.speech, current_speaker.profile.identity.name)

        # D. Swap turns
        current_speaker, other_agent = other_agent, current_speaker


if __name__ == "__main__":
    main()
