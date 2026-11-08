import pytest

from agent.domain.task.task_status import ALLOWED_TRANSITIONS, TaskStatus, is_terminal


def test_every_status_has_a_rule():
    assert set(ALLOWED_TRANSITIONS) == set(TaskStatus)


def test_done_and_failed_are_terminal():
    assert is_terminal(TaskStatus.DONE)
    assert is_terminal(TaskStatus.FAILED)


@pytest.mark.parametrize(
    "status",
    [s for s in TaskStatus if s not in (TaskStatus.DONE, TaskStatus.FAILED)],
)
def test_other_statuses_are_not_terminal(status):
    assert not is_terminal(status)
