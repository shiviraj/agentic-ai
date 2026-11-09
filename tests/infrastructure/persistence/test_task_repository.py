import pytest
from agent.domain.task.task import Task
from agent.domain.task.task_id import TaskId
from agent.infrastructure.persistence.task_repository import (
    InMemoryTaskRepository,
)

from agent.domain.errors import TaskNotFoundError


def test_save_and_get():
    repo = InMemoryTaskRepository()
    task = Task(id=TaskId.generate(), prompt="x")
    repo.save(task)
    assert repo.get(task.id) is task


def test_missing_task_raises():
    with pytest.raises(TaskNotFoundError):
        InMemoryTaskRepository().get("nope")


def test_list_all():
    repo = InMemoryTaskRepository()
    a, b = Task(id=TaskId.generate(), prompt="a"), Task(id=TaskId.generate(), prompt="b")
    repo.save(a)
    repo.save(b)
    assert set(t.id for t in repo.list_all()) == {a.id, b.id}
