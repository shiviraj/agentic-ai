from typing import Protocol

from agent.domain.entity.plan_step import PlanStep


class StepExecutor(Protocol):
    def execute(self, step: PlanStep) -> None:
        ...