import os
from pathlib import Path
from ollama import Client
from prompt_toolkit import PromptSession
from rich.console import Console
from agent.application.services.create_plan import CreatePlan
from agent.application.services.execute_plan import ExecutePlan
from agent.application.services.tool_executor import ToolExecutor
from agent.application.workflow.progress_prompt_workflow import ProcessPromptWorkflow
from agent.domain.policy.tool_approval_policy import ToolApprovalPolicy
from agent.infrastructure.cli_approval_gateway import CliApprovalGateway
from agent.infrastructure.create_tool_registry import create_tool_registry
from agent.infrastructure.ollama_planner import OllamaPlanner
from agent.infrastructure.tool_step_executor import ToolStepExecutor
from agent.interface.cli.app import PROMPT_INSTRUCTIONS
from agent.interface.cli.display_plan import display_plan, display_tool_execution, display_tool_result, \
    display_step_executing
from agent.interface.cli.prompt_input import create_prompt_session, user_prompt


def main() -> None:
    client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), timeout=120)
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    console = Console()
    registry = create_tool_registry(Path('workspace'))

    tool_executor = ToolExecutor(
        ToolApprovalPolicy(),
        CliApprovalGateway(console),
        display_tool_execution=display_tool_execution,
        display_tool_result=display_tool_result
    )
    planner = OllamaPlanner(client, model=model, tool_registry=registry, console=console)
    step_executor = ToolStepExecutor(client, model, registry, console)

    create_plan = CreatePlan(planner=planner, display_plan=display_plan, tool_executor=tool_executor)
    execute_plan = ExecutePlan(
        step_executor=step_executor,
        tool_executor=tool_executor,
        display_step_executing=display_step_executing
    )
    workflow = ProcessPromptWorkflow(create_plan=create_plan, execute_plan=execute_plan)

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
