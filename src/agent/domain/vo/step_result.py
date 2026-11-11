from dataclasses import dataclass

from agent.domain.entity.sub_task import PlanStep


@dataclass
class StepResult:
    success: bool
    step: PlanStep
    data: dict[str, object] | None = None
    error: str | None = None
