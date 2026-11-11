from dataclasses import dataclass
from uuid import UUID, uuid4

from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True)
class SubTaskId(ValueObject):
    value: UUID

    @classmethod
    def generate(cls) -> "SubTaskId":
        return cls(value=uuid4())
