from typing import Protocol

from agent.domain.entity.plan_step import PlanStep


class StepApproval(Protocol):
    def approve(self, step: PlanStep) -> bool:
        ...
