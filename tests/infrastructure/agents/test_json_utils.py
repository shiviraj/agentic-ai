import pytest

from agent.domain.errors import InvalidAgentOutputError
from agent.infrastructure.agents.json_utils import parse_json_object


def test_plain_json():
    assert parse_json_object('{"a": 1}') == {"a": 1}


def test_json_inside_code_fence():
    assert parse_json_object('```json\n{"a": 1}\n```') == {"a": 1}


def test_json_with_chatter_around_it():
    assert parse_json_object('Sure! Here it is: {"a": 1} Hope it helps.') == {"a": 1}


@pytest.mark.parametrize("bad", ["not json", "", "[1, 2, 3]", '"text"', "{broken"])
def test_bad_input_raises(bad):
    with pytest.raises(InvalidAgentOutputError):
        parse_json_object(bad)
