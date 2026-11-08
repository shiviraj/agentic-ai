import pytest
from tests.fakes.fake_agent import FakeAgent
from tests.fakes.fake_user_interaction import FakeUserInteraction

from agent.application.manager.manager_service import ManagerService
from agent.application.manager.retry_policy import RetryPolicy
from agent.domain.agent.agent_result import AgentResult
from agent.domain.agent.agent_role import AgentRole
from agent.domain.task.task import Task
from agent.domain.task.task_id import TaskId
from agent.domain.task.task_status import TaskStatus
from agent.infrastructure.persistence.task_repository import (
    InMemoryTaskRepository,
)

A, P, C, R, Q = (
    AgentRole.ANALYSER,
    AgentRole.PLANNER,
    AgentRole.CODER,
    AgentRole.REVIEWER,
    AgentRole.QA,
)


def build(results=None, errors=None, policy=None, answers=None, skip=()):
    """Make a Manager with fake agents. `results`/`errors` are per role."""
    results = results or {}
    errors = errors or {}
    log: list[AgentRole] = []
    agents = {
        role: FakeAgent(role, results.get(role), log=log, error=errors.get(role))
        for role in AgentRole
        if role not in skip
    }
    repo = InMemoryTaskRepository()
    user = FakeUserInteraction(answers)
    manager = ManagerService(list(agents.values()), repo, user, policy)
    return manager, agents, repo, user, log


def new_task() -> Task:
    return Task(id=TaskId.generate(), prompt="implement healthcheck endpoint")


# ---- happy path ---------------------------------------------------


def test_happy_path_runs_every_agent_in_order():
    manager, _, _, _, log = build()
    task = manager.run(new_task())

    assert task.status == TaskStatus.DONE
    assert log == [A, P, C, R, Q]


def test_requirements_and_plan_are_saved_on_the_task():
    manager, *_ = build()
    task = manager.run(new_task())

    assert task.requirements == "ANALYSER output"
    assert task.plan == "PLANNER output"


def test_final_task_is_saved_in_the_repository():
    manager, _, repo, _, _ = build()
    task = manager.run(new_task())
    assert repo.get(task.id).status == TaskStatus.DONE


def test_finished_task_is_not_run_again():
    manager, _, _, _, log = build()
    task = new_task()
    task.status = TaskStatus.DONE
    manager.run(task)
    assert log == []


# ---- clarification loop -------------------------------------------


def test_questions_are_asked_and_analyser_runs_again():
    manager, agents, _, user, _ = build(
        results={A: [AgentResult.needs_clarification(["Which port?"]), AgentResult.done("REQ")]},
        answers=["3000"],
    )
    task = manager.run(new_task())

    assert task.status == TaskStatus.DONE
    assert user.asked == ["Which port?"]
    assert task.clarifications == [("Which port?", "3000")]
    assert agents[A].calls == 2
    assert task.requirements == "REQ"


def test_too_many_clarification_rounds_fail_the_task():
    manager, agents, _, user, _ = build(
        results={A: [AgentResult.needs_clarification(["Q?"])]},
        policy=RetryPolicy(max_clarification_rounds=2),
    )
    task = manager.run(new_task())

    assert task.status == TaskStatus.FAILED
    assert "unclear" in task.failure_reason
    assert agents[A].calls == 3
    assert len(user.asked) == 2


# ---- review loop ---------------------------------------------------


def test_rejected_review_sends_work_back_to_coder_with_feedback():
    manager, agents, _, _, _ = build(
        results={R: [AgentResult.rejected("fix A"), AgentResult.rejected("fix B"), AgentResult.done("ok")]}
    )
    task = manager.run(new_task())

    assert task.status == TaskStatus.DONE
    assert agents[C].calls == 3
    assert agents[C].seen_feedback == [None, "fix A", "fix B"]
    assert task.feedback is None  # cleared once the coder used it
    assert task.retries("review") == 2


def test_review_that_never_passes_fails_the_task():
    manager, agents, _, _, _ = build(
        results={R: [AgentResult.rejected("still bad")]},
        policy=RetryPolicy(max_review_retries=2),
    )
    task = manager.run(new_task())

    assert task.status == TaskStatus.FAILED
    assert agents[C].calls == 3
    assert agents[R].calls == 3
    assert "review" in task.failure_reason
    assert "still bad" in task.failure_reason


# ---- QA loop -------------------------------------------------------


def test_failed_tests_send_work_back_and_through_review_again():
    manager, agents, _, _, log = build(results={Q: [AgentResult.rejected("test failed"), AgentResult.done("ok")]})
    task = manager.run(new_task())

    assert task.status == TaskStatus.DONE
    assert log == [A, P, C, R, Q, C, R, Q]
    assert agents[C].seen_feedback == [None, "test failed"]


def test_qa_that_never_passes_fails_the_task():
    manager, agents, _, _, _ = build(
        results={Q: [AgentResult.rejected("broken")]},
        policy=RetryPolicy(max_qa_retries=1),
    )
    task = manager.run(new_task())

    assert task.status == TaskStatus.FAILED
    assert agents[C].calls == 2
    assert "qa" in task.failure_reason


# ---- failures and safety nets -------------------------------------


def test_failed_agent_fails_the_task():
    manager, agents, _, _, _ = build(results={P: [AgentResult.failed("model crashed")]})
    task = manager.run(new_task())

    assert task.status == TaskStatus.FAILED
    assert "model crashed" in task.failure_reason
    assert agents[C].calls == 0


def test_crashing_agent_fails_the_task_without_crashing_the_loop():
    manager, agents, _, _, _ = build(errors={C: RuntimeError("boom")})
    task = manager.run(new_task())

    assert task.status == TaskStatus.FAILED
    assert "boom" in task.failure_reason
    assert agents[R].calls == 0


def test_missing_agent_fails_the_task_with_a_clear_reason():
    manager, _, _, _, _ = build(skip=(P,))
    task = manager.run(new_task())

    assert task.status == TaskStatus.FAILED
    assert "PLANNER" in task.failure_reason
    assert task.requirements == "ANALYSER output"  # earlier work is kept


def test_step_limit_stops_the_loop():
    manager, _, _, _, log = build(policy=RetryPolicy(max_total_steps=3))
    task = manager.run(new_task())

    assert task.status == TaskStatus.FAILED
    assert "steps" in task.failure_reason
    assert len(log) == 3


def test_clarification_from_the_wrong_agent_is_not_allowed():
    manager, _, _, _, _ = build(results={C: [AgentResult.needs_clarification(["?"])]})
    assert manager.run(new_task()).status == TaskStatus.FAILED


def test_rejection_from_the_wrong_agent_is_not_allowed():
    manager, _, _, _, _ = build(results={P: [AgentResult.rejected("no")]})
    assert manager.run(new_task()).status == TaskStatus.FAILED


def test_two_agents_for_the_same_role_are_rejected():
    with pytest.raises(ValueError):
        ManagerService(
            [FakeAgent(A), FakeAgent(A)],
            InMemoryTaskRepository(),
            FakeUserInteraction(),
        )
