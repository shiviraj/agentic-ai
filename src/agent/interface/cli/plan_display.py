from rich.console import Console

from agent.domain.aggregate.implementation_plan import ImplementationPlan


def display_plan(plan: ImplementationPlan) -> None:
    console = Console()
    """Present a generated plan without changing domain state."""
    console.print("\n[bold green]Plan generated successfully.[/bold green]")
    console.print(f"Plan ID: {plan.id.value}\tStatus: {plan.status}")
    console.print("\n[bold]Implementation steps[/bold]")
    for step in plan.steps:
        console.print(f"  {step.sequence}. {step.title}")
    console.print()
