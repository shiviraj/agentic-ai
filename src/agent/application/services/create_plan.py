from typing import Callable

from agent.application.port.planner import Planner
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.prompt import Prompt


class CreatePlan:
    def __init__(self, planner: Planner, display_plan: Callable[[ImplementationPlan], None]) -> None:
        self._planner = planner
        self._display_plan = display_plan

    def execute(self, prompt: Prompt) -> ImplementationPlan:
        analysis_result = self._planner.analyze_requirement(prompt)
        context = self._planner.discover_context(analysis_result, prompt)
        proposal = self._planner.create_proposal(context=context, prompt=prompt)

        steps = [
            PlanStep.create(title=step.title, description=step.description, sequence=index)
            for index, step in enumerate(proposal, start=1)
        ]

        plan = ImplementationPlan.create(steps=steps)
        self._display_plan(plan)
        return plan
