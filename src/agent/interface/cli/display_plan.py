from rich.console import Console

from agent.application.tool.tool import Tool
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.tool_result import ToolResult


def display_plan(plan: ImplementationPlan) -> None:
    console = Console()
    """Present a generated plan without changing domain state."""
    # console.print(f"Plan ID: {plan.id.value}\tStatus: {plan.status}")
    console.print("[bold]Implementation steps[/bold]")
    for step in plan.steps:
        console.print(f"  {step.sequence}. {step.title}")


def display_tool_result(tool_result: ToolResult) -> None:
    console = Console()
    if tool_result.success:
        console.print(f"[green]Tool executed successfully\tdata: {tool_result.data}[/green]")
    else:
        console.print(f"[red]Failed to execute tool\tError: {tool_result.error}[/red]")


def display_tool_execution(tool: Tool, arguments: dict[str, object]) -> None:
    console = Console()
    console.print(f"Tool execution started")
    console.print(f"Tool: {tool.display_name} \tRisk: {tool.tool_risk}")
    arguments_display_text = tool.display_arguments(arguments)
    if arguments_display_text:
        console.print(f"\tArguments: {arguments_display_text}")


def display_step_executing(step: PlanStep) -> None:
    console = Console()
    console.print()
    console.print(f"[cyan]{step.sequence}. {step.title}\n{step.description}[/cyan]")
