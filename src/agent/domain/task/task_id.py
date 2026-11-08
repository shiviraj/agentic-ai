from dataclasses import dataclass
from uuid import UUID, uuid4

from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True)
class TaskId(ValueObject):
    value: UUID

    @staticmethod
    def generate() -> "TaskId":
        return TaskId(value=uuid4())
