from dataclasses import dataclass

from agent.domain.vo.task_id import TaskId
from agent.domain.vo.task_status import TaskStatus


@dataclass(frozen=True)
class SubmitPromptResult:
    task_id: TaskId
    status: TaskStatus
