from dataclasses import dataclass
from uuid import UUID, uuid4

from agent.shared.domain.entity import Entity


@dataclass(eq=False)
class PlanStep(Entity[UUID]):
    description: str
    sequence: int

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Plan step description cannot be empty")

        if self.sequence < 1:
            raise ValueError("Plan step sequence must start at 1")

    @classmethod
    def create(cls, description: str, sequence: int, ) -> "PlanStep":
        return cls(id=uuid4(), description=description, sequence=sequence)
