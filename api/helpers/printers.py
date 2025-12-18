from services.agent import Agent
from rich.console import Console

console = Console()


def print_memory_state(agent: Agent, memory_type: str) -> None:
    """Helper function to print the state of an agent's memory."""
    if memory_type == "short_term":
        memory = agent.short_term_memory
    elif memory_type == "mid_term":
        memory = agent.mid_term_memory
    elif memory_type == "long_term":
        memory = agent.long_term_memory
    else:
        raise ValueError("Invalid memory type specified.")

    console.print(
        f"[bold blue]{agent.profile.identity.name}'s {memory_type.replace('_', ' ').title()} Memory:[/bold blue]"
    )
    for item in memory:
        console.print(f"- {item}")
