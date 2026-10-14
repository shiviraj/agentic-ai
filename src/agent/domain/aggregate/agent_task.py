from dataclasses import dataclass, field
from datetime import datetime, timezone

from agent.domain.vo.prompt import Prompt
from agent.domain.vo.task_id import TaskId
from agent.domain.vo.task_status import TaskStatus
from agent.shared.domain.aggregate import Aggregate


@dataclass(eq=False)
class AgentTask(Aggregate[TaskId]):
    prompt: Prompt
    status: TaskStatus = TaskStatus.SUBMITTED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
