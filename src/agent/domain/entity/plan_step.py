from dataclasses import dataclass

from agent.domain.vo.step_id import StepId
from agent.shared.domain.entity import Entity


@dataclass(eq=False)
class PlanStep(Entity[StepId]):
    title: str
    description: str
    sequence: int

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Plan step description cannot be empty")

        if self.sequence < 1:
            raise ValueError("Plan step sequence must start at 1")

    @classmethod
    def create(cls, title: str, description: str, sequence: int) -> "PlanStep":
        return cls(id=StepId.generate(), title=title, description=description, sequence=sequence)
