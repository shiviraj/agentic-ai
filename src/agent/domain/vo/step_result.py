from dataclasses import dataclass

from agent.domain.entity.interaction import PlanStep


@dataclass
class StepResult:
    success: bool
    step: PlanStep
    data: dict[str, object] | None = None
    error: str | None = None
