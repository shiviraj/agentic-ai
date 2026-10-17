from dataclasses import dataclass, field
from datetime import datetime, timezone

from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.plan_id import PlanId
from agent.domain.vo.plan_status import PlanStatus
from agent.shared.domain.aggregate import Aggregate


@dataclass(eq=False)
class ImplementationPlan(Aggregate[PlanId]):
    steps: list[PlanStep]
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.steps:
            raise ValueError("An implementation plan must contain steps")

        sequences = [step.sequence for step in self.steps]

        if len(sequences) != len(set(sequences)):
            raise ValueError("Plan step sequences must be unique")

        self.steps.sort(key=lambda step: step.sequence)

    @classmethod
    def create(cls, steps: list[PlanStep]) -> "ImplementationPlan":
        return cls(id=PlanId.generate(), steps=steps)
