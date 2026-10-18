from dataclasses import dataclass

from agent.application.services.create_plan import CreatePlan
from agent.application.services.execute_plan import ExecutePlan
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId


@dataclass(frozen=True)
class ProcessPromptResult:
    task_id: TaskId
    plan: object


class ProcessPromptWorkflow:
    def __init__(self, create_plan: CreatePlan, execute_plan: ExecutePlan) -> None:
        self._create_plan = create_plan
        self._execute_plan = execute_plan

    def execute(self, prompt: Prompt) -> None:
        plan = self._create_plan.execute(prompt=prompt)
        self._execute_plan.execute(plan=plan)
        # return ProcessPromptResult(plan=plan)
