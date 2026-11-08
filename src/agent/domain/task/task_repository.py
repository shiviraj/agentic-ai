from abc import ABC, abstractmethod

from agent.domain.task.task import Task


class TaskRepository(ABC):
    @abstractmethod
    def save(self, task: Task) -> None: ...

    @abstractmethod
    def get(self, task_id: str) -> Task:
        """Return the task, or raise TaskNotFoundError."""

    @abstractmethod
    def list_all(self) -> list[Task]: ...
