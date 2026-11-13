from dataclasses import dataclass
from enum import Enum

from agent.domain.vo.subtask_id import SubtaskId
from agent.shared.domain.entity import Entity


class SubTaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=False)
class Subtask(Entity[SubtaskId]):
    sequence: int
    title: str
    description: str
    status: SubTaskStatus = SubTaskStatus.PENDING

    @classmethod
    def create(
        cls,
        sequence: int,
        title: str,
        description: str,
    ) -> "Subtask":
        return cls(
            id=SubtaskId.generate(),
            sequence=sequence,
            title=title,
            description=description,
            status=SubTaskStatus.PENDING,
        )
