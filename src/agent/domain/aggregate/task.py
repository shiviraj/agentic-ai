from dataclasses import dataclass
from enum import Enum

from agent.domain.entity.subtask import Subtask
from agent.domain.vo.task_id import TaskId
from agent.shared.domain.aggregate import Aggregate


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=False)
class Task(Aggregate[TaskId]):
    title: str
    description: str
    sub_tasks: tuple[Subtask, ...]
    status: TaskStatus = TaskStatus.PENDING

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        sub_tasks: tuple[Subtask, ...],
    ) -> "Task":
        return cls(
            id=TaskId.generate(), title=title, description=description, sub_tasks=sub_tasks, status=TaskStatus.PENDING
        )
