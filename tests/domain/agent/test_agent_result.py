import dataclasses

import pytest

from agent.domain.agent.agent_result import AgentResult, ResultStatus


def test_done_helper():
    result = AgentResult.done("all good")
    assert result.status == ResultStatus.DONE
    assert result.output == "all good"
    assert result.questions == ()


def test_failed_helper():
    result = AgentResult.failed("model crashed")
    assert result.status == ResultStatus.FAILED
    assert result.output == "model crashed"


def test_needs_clarification_stores_questions_as_tuple():
    result = AgentResult.needs_clarification(["Which port?", "Which framework?"])
    assert result.status == ResultStatus.NEEDS_CLARIFICATION
    assert result.questions == ("Which port?", "Which framework?")
    assert isinstance(result.questions, tuple)


def test_result_cannot_be_changed():
    result = AgentResult.done("x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.output = "changed"  # type: ignore[misc]


def test_rejected_helper():
    result = AgentResult.rejected("rename the function")
    assert result.status == ResultStatus.REJECTED
    assert result.output == "rename the function"
