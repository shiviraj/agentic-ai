from dataclasses import dataclass
from uuid import UUID, uuid4

from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True)
class InteractionId(ValueObject):
    value: UUID

    @classmethod
    def generate(cls) -> "InteractionId":
        return cls(value=uuid4())
