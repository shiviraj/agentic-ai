import pytest
from agent.application.manager.retry_policy import RetryPolicy


def test_defaults_are_sensible():
    policy = RetryPolicy()
    assert policy.limit_for("review") == 3
    assert policy.limit_for("qa") == 3
    assert policy.limit_for("clarification") == 3


def test_limits_can_be_changed():
    policy = RetryPolicy(max_review_retries=1, max_qa_retries=2)
    assert policy.limit_for("review") == 1
    assert policy.limit_for("qa") == 2


@pytest.mark.parametrize(
    "field",
    [
        "max_review_retries",
        "max_qa_retries",
        "max_clarification_rounds",
        "max_total_steps",
    ],
)
def test_negative_limits_are_rejected(field):
    with pytest.raises(ValueError):
        RetryPolicy(**{field: -1})
