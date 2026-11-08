from dataclasses import dataclass, field

from agent.domain.errors import InvalidStatusTransitionError
from agent.domain.task.task_id import TaskId
from agent.domain.task.task_status import ALLOWED_TRANSITIONS, TaskStatus
from agent.shared.domain.entity import Entity


@dataclass
class Task(Entity[TaskId]):
    prompt: str
    status: TaskStatus = TaskStatus.ANALYSING
    requirements: str | None = None
    plan: str | None = None
    retry_counts: dict[str, int] = field(default_factory=dict)
    clarifications: list[tuple[str, str]] = field(default_factory=list)
    feedback: str | None = None
    failure_reason: str | None = None

    def move_to(self, new_status: TaskStatus) -> None:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise InvalidStatusTransitionError(
                f"Cannot move task {self.id} from {self.status.value} to {new_status.value}"
            )
        self.status = new_status

    def increment_retry(self, loop_name: str) -> int:
        self.retry_counts[loop_name] = self.retry_counts.get(loop_name, 0) + 1
        return self.retry_counts[loop_name]

    def retries(self, loop_name: str) -> int:
        return self.retry_counts.get(loop_name, 0)

    def attach_requirements(self, text: str) -> None:
        self.requirements = text

    def attach_plan(self, text: str) -> None:
        self.plan = text

    def add_clarification(self, question: str, answer: str) -> None:
        self.clarifications.append((question, answer))

    def set_feedback(self, text: str) -> None:
        self.feedback = text

    def clear_feedback(self) -> None:
        self.feedback = None

    def fail(self, reason: str) -> None:
        self.move_to(TaskStatus.FAILED)
        self.failure_reason = reason
