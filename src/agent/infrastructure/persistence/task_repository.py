from agent.domain.errors import TaskNotFoundError
from agent.domain.task.task import Task
from agent.domain.task.task_repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(f"No task with id {task_id}") from None

    def list_all(self) -> list[Task]:
        return list(self._tasks.values())
