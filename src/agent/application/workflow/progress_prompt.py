from dataclasses import dataclass

from agent.application.services.create_plan import CreatePlan
from agent.application.services.submit_prompt import SubmitPrompt
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId


@dataclass(frozen=True)
class ProcessPromptResult:
    task_id: TaskId
    plan: object


class ProcessPrompt:
    def __init__(self, submit_prompt: SubmitPrompt, create_plan: CreatePlan) -> None:
        self._submit_prompt = submit_prompt
        self._create_plan = create_plan

    def execute(self, prompt: Prompt) -> ProcessPromptResult:
        task = self._submit_prompt.execute(prompt)

        plan = self._create_plan.execute(task_id=task.task_id, prompt=prompt)

        return ProcessPromptResult(task_id=task.task_id, plan=plan, )
