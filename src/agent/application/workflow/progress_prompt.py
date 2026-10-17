from dataclasses import dataclass

from agent.application.services.create_plan import CreatePlan
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId


@dataclass(frozen=True)
class ProcessPromptResult:
    task_id: TaskId
    plan: object


class ProcessPromptWorkflow:
    def __init__(self, create_plan: CreatePlan) -> None:
        # self._submit_prompt = submit_prompt
        self._create_plan = create_plan

    def execute(self, prompt: Prompt) -> None:
        plan = self._create_plan.execute(prompt=prompt)
        # return ProcessPromptResult(plan=plan)
