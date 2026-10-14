from agent.application.services.create_plan import CreatePlan
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId
from agent.infrastructure.ollama_planner import OllamaPlanner
from agent.interface.cli.app import run_cli


def main() -> None:
    planner = OllamaPlanner()
    create_plan = CreatePlan(planner=planner)

    def process_prompt(prompt: Prompt):
        return create_plan.execute(TaskId.generate(), prompt)

    run_cli(process_prompt)
