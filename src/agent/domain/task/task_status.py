from enum import Enum


class TaskStatus(str, Enum):
    ANALYSING = "ANALYSING"
    PLANNING = "PLANNING"
    CODING = "CODING"
    REVIEWING = "REVIEWING"
    TESTING = "TESTING"
    DONE = "DONE"
    FAILED = "FAILED"


ALLOWED_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.ANALYSING: frozenset({TaskStatus.PLANNING, TaskStatus.FAILED}),
    TaskStatus.PLANNING: frozenset({TaskStatus.CODING, TaskStatus.FAILED}),
    TaskStatus.CODING: frozenset({TaskStatus.REVIEWING, TaskStatus.FAILED}),
    TaskStatus.REVIEWING: frozenset({TaskStatus.CODING, TaskStatus.TESTING, TaskStatus.FAILED}),
    TaskStatus.TESTING: frozenset(
        {
            TaskStatus.CODING,
            TaskStatus.PLANNING,
            TaskStatus.DONE,
            TaskStatus.FAILED,
        }
    ),
    TaskStatus.DONE: frozenset(),
    TaskStatus.FAILED: frozenset(),
}


def is_terminal(status: TaskStatus) -> bool:
    """A terminal status is one the task can never leave."""
    return not ALLOWED_TRANSITIONS[status]
