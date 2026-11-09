import pytest
from agent.domain.task.task import Task
from agent.domain.task.task_id import TaskId
from agent.domain.task.task_status import ALLOWED_TRANSITIONS, TaskStatus

from agent.domain.errors import InvalidStatusTransitionError


def make_task_in(status: TaskStatus) -> Task:
    task = Task(id=TaskId.generate(), prompt="implement health check endpoint")
    task.status = status  # set directly just for test setup
    return task


def test_new_task_starts_as_analysing():
    task = Task(id=TaskId.generate(), prompt="implement health check endpoint")
    assert task.status == TaskStatus.ANALYSING
    assert task.requirements is None
    assert task.plan is None


def test_each_task_gets_its_own_id():
    assert Task(id=TaskId.generate(), prompt="a").id != Task(id=TaskId.generate(), prompt="b").id


@pytest.mark.parametrize(
    "start,target",
    [(s, t) for s, targets in ALLOWED_TRANSITIONS.items() for t in targets],
)
def test_allowed_moves_work(start, target):
    task = make_task_in(start)
    task.move_to(target)
    assert task.status == target


def test_forbidden_move_raises():
    task = make_task_in(TaskStatus.ANALYSING)
    with pytest.raises(InvalidStatusTransitionError):
        task.move_to(TaskStatus.DONE)


@pytest.mark.parametrize("terminal", [TaskStatus.DONE, TaskStatus.FAILED])
@pytest.mark.parametrize("target", list(TaskStatus))
def test_nothing_leaves_a_terminal_status(terminal, target):
    task = make_task_in(terminal)
    with pytest.raises(InvalidStatusTransitionError):
        task.move_to(target)


def test_retry_counting():
    task = Task(id=TaskId.generate(), prompt="x")
    assert task.retries("review") == 0
    assert task.increment_retry("review") == 1
    assert task.increment_retry("review") == 2
    assert task.retries("review") == 2
    assert task.retries("qa") == 0


def test_tasks_do_not_share_retry_counts():
    a = Task(id=TaskId.generate(), prompt="a")
    b = Task(id=TaskId.generate(), prompt="b")
    a.increment_retry("review")
    assert b.retries("review") == 0


def test_attach_requirements_and_plan():
    task = Task(id=TaskId.generate(), prompt="x")
    task.attach_requirements("GET /healthcheck returns 200")
    task.attach_plan("1. add route 2. add test")
    assert task.requirements == "GET /healthcheck returns 200"
    assert task.plan == "1. add route 2. add test"


def test_clarifications_are_stored_per_task():
    a = Task(id=TaskId.generate(), prompt="a")
    b = Task(id=TaskId.generate(), prompt="b")
    a.add_clarification("Which port?", "3000")
    assert a.clarifications == [("Which port?", "3000")]
    assert b.clarifications == []


def test_fail_sets_status_and_reason():
    task = Task(id=TaskId.generate(), prompt="x")
    task.fail("something broke")
    assert task.status == TaskStatus.FAILED
    assert task.failure_reason == "something broke"


def test_feedback_can_be_set_and_cleared():
    task = Task(id=TaskId.generate(), prompt="x")
    task.set_feedback("add a test")
    assert task.feedback == "add a test"
    task.clear_feedback()
    assert task.feedback is None
