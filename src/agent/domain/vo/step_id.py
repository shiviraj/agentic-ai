from dataclasses import dataclass
from uuid import UUID, uuid4

from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True)
class StepId(ValueObject):
    value: UUID

    @classmethod
    def generate(cls) -> "StepId":
        return cls(value=uuid4())
