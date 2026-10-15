from rich.console import Console

from agent.application.port import step_executor
from agent.application.services import plan_executor
from agent.application.services.create_plan import CreatePlan
from agent.application.services.plan_executor import PlanExecutor
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId
from agent.infrastructure.ollama_planner import OllamaPlanner
from agent.infrastructure.unavailable_step_executor import UnavailableStepExecutor
from agent.interface.cli.app import run_cli
from agent.interface.cli.approval import CliStepApproval


def main() -> None:
    create_plan = CreatePlan(planner=(OllamaPlanner()))
    plan_executor = PlanExecutor(
        step_executor=UnavailableStepExecutor(),
        step_approval=CliStepApproval(console=Console())
    )

    def process_prompt(prompt: Prompt):
        return create_plan.execute(TaskId.generate(), prompt)

    def execute_plan(plan: ImplementationPlan) -> None:
        plan_executor.execute(plan)

    run_cli(process_prompt, execute_plan)
