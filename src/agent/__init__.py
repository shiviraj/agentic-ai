import contextlib
import os
from pathlib import Path
from ollama import Client
from prompt_toolkit import PromptSession
from rich.console import Console
from agent.application.port import step_executor
from agent.application.services import plan_executor
from agent.application.services.create_plan import CreatePlan
from agent.application.services.plan_executor import PlanExecutor
from agent.application.workflow.progress_prompt import ProcessPromptWorkflow
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId
from agent.infrastructure.create_tool_registry import create_tool_registry
from agent.infrastructure.ollama_planner import OllamaPlanner
from agent.infrastructure.tool_step_executor import ToolStepExecutor
from agent.interface.cli.app import PROMPT_INSTRUCTIONS
from agent.interface.cli.approval import CliStepApproval
from agent.interface.cli.plan_display import display_plan
from agent.interface.cli.prompt_input import create_prompt_session, user_prompt


def main() -> None:
    client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), timeout=120)
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    console = Console()
    registry = create_tool_registry(Path('workspace'))

    planner = OllamaPlanner(client, model=model, tool_registry=registry, console=console)
    create_plan = CreatePlan(planner=planner, display_plan=display_plan)
    workflow = ProcessPromptWorkflow(create_plan=create_plan)

    executor = PlanExecutor(
        step_executor=ToolStepExecutor(client, model, registry, console),
        step_approval=CliStepApproval(console=console)
    )

    session: PromptSession[str] = create_prompt_session()
    console.print(PROMPT_INSTRUCTIONS, style="cyan")

    try:
        while True:
            should_exit, prompt = user_prompt(session)
            if should_exit:
                console.print(prompt.value, style="dim")
                break
            if not prompt:
                continue
            try:
                workflow.execute(prompt)
            except KeyboardInterrupt:
                console.print("\n[yellow]Request interrupted.[/yellow]\n")
            except Exception:
                console.print("\n[bold red]Failed to process the request.[/bold red]")
                console.print("[dim]Check the application logs for details.[/dim]\n")

    except KeyboardInterrupt:
        pass
