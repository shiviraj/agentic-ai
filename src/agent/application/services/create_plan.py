from agent.application.port.planner import Planner
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId


class CreatePlan:
    def __init__(self, planner: Planner) -> None:
        self._planner = planner

    def execute(self, task_id: TaskId, prompt: Prompt) -> ImplementationPlan:
        proposal = self._planner.generate_plan(prompt)

        steps = [
            PlanStep.create(description=proposed_step.description, sequence=index)
            for index, proposed_step in enumerate(proposal.steps, start=1)
        ]

        return ImplementationPlan.create(task_id=task_id, steps=steps)
