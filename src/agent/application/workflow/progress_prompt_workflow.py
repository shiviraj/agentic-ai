from dataclasses import dataclass

from agent.application.workflow.create_plan_workflow import CreatePlanWorkflow
from agent.application.workflow.execute_plan_workflow import ExecutePlanWorkflow
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId


@dataclass(frozen=True)
class ProcessPromptResult:
    task_id: TaskId
    plan: object


class ProcessPromptWorkflow:
    def __init__(self, create_plan_workflow: CreatePlanWorkflow, execute_plan_workflow: ExecutePlanWorkflow) -> None:
        self._create_plan_workflow = create_plan_workflow
        self._execute_plan_workflow = execute_plan_workflow

    def execute(self, prompt: Prompt) -> None:
        plan = self._create_plan_workflow.execute(prompt=prompt)
        self._execute_plan_workflow.execute(plan=plan)
