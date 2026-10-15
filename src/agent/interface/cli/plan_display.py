import rich

from agent.domain.aggregate.implementation_plan import ImplementationPlan


def display_plan(plan: ImplementationPlan, console: rich.Console) -> None:
    """Present a generated plan without changing domain state."""
    console.print("\n[bold green]Plan generated successfully.[/bold green]")
    console.print(f"Plan ID: {plan.id.value}")
    console.print(f"Status: {plan.status}")
    console.print("\n[bold]Implementation steps[/bold]")
    for step in plan.steps:
        console.print(f"  {step.sequence}. {step.title}")
    console.print()
