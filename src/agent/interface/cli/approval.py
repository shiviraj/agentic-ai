from rich.console import Console

from agent.application.port.step_approval import StepApproval
from agent.domain.entity.plan_step import PlanStep


class CliStepApproval(StepApproval):
    def __init__(self, console: Console) -> None:
        self._console = console

    def approve(self, step: PlanStep) -> bool:
        self._console.print(f"\n[bold]Step {step.sequence}[/bold]: {step.title}\n  {step.description}")
        answer = self._console.input("[yellow]Execute this step? \\[y/N]: [/yellow]").strip().lower()
        if answer == "y":
            return True
        self._console.print("[dim]Step declined. Remaining steps will not execute.[/dim]")
        return False
