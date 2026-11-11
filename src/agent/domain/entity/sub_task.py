from dataclasses import dataclass
from enum import Enum

from agent.domain.vo.sub_task_id import SubTaskId
from agent.shared.domain.entity import Entity


class SubTaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=False)
class SubTask(Entity[SubTaskId]):
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
    ) -> "SubTask":
        return cls(
            id=SubTaskId.generate(),
            sequence=sequence,
            title=title,
            description=description,
            status=SubTaskStatus.PENDING,
        )
