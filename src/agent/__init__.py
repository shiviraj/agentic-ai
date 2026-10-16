import contextlib
import os
from pathlib import Path
from ollama import Client
from rich.console import Console
from agent.application.port import step_executor
from agent.application.services import plan_executor
from agent.application.services.create_plan import CreatePlan
from agent.application.services.plan_executor import PlanExecutor
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId
from agent.infrastructure.create_tool_registry import create_tool_registry
from agent.infrastructure.ollama_planner import OllamaPlanner
from agent.infrastructure.tool_step_executor import ToolStepExecutor
from agent.interface.cli.app import run_cli
from agent.interface.cli.approval import CliStepApproval


def main() -> None:
    client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), timeout=120)
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    console = Console()
    registry = create_tool_registry(Path('workspace'))

    create_plan = CreatePlan(planner=(OllamaPlanner(client, model=model, tool_registry=registry, console=console)))
    executor = PlanExecutor(
        step_executor=ToolStepExecutor(client, model, registry, console),
        step_approval=CliStepApproval(console=console)
    )

    def process_prompt(prompt: Prompt):
        return create_plan.execute(TaskId.generate(), prompt)

    def execute_plan(plan: ImplementationPlan) -> None:
        executor.execute(plan)

    run_cli(process_prompt, execute_plan)
