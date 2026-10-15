from collections.abc import Callable

from rich.console import Console

from agent.domain.aggregate.implementation_plan import ImplementationPlan


def execute_plan(plan: ImplementationPlan, executor: Callable[[ImplementationPlan], None], console: Console, ) -> None:
    try:
        executor(plan)
        console.print("[bold green]Plan execution completed.[/bold green]")

    except NotImplementedError as exc:
        console.print(f"[yellow]{exc}[/yellow]")

    except Exception:
        console.print("\n[bold red]Step execution failed.[/bold red]")
        console.print("[dim]Check the application logs for details.[/dim]")
