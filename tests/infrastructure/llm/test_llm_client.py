from types import SimpleNamespace

import httpx
import ollama
import pytest

from agent.domain.errors import LlmUnavailableError
from agent.domain.llm.message import Message, Role
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl


class FakeOllama:
    def __init__(self, content="hello", error=None):
        self._content = content
        self._error = error
        self.last_kwargs = None

    def chat(self, **kwargs):
        self.last_kwargs = kwargs
        if self._error:
            raise self._error
        return SimpleNamespace(message=SimpleNamespace(content=self._content))


MESSAGES = [
    Message(Role.SYSTEM, "You are helpful."),
    Message(Role.USER, "Say hi"),
]


def make_client(fake: FakeOllama) -> LLMClientImpl:
    return LLMClientImpl(model="test-model", num_ctx=4096, client=fake)


def test_returns_the_model_text():
    assert make_client(FakeOllama("hi there")).chat(MESSAGES) == "hi there"


def test_messages_are_converted_to_plain_dicts():
    fake = FakeOllama()
    make_client(fake).chat(MESSAGES)
    assert fake.last_kwargs["messages"] == [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Say hi"},
    ]


def test_num_ctx_and_model_are_sent():
    fake = FakeOllama()
    make_client(fake).chat(MESSAGES)
    assert fake.last_kwargs["model"] == "test-model"
    assert fake.last_kwargs["options"]["num_ctx"] == 4096


def test_json_mode_sets_format():
    fake = FakeOllama()
    client = make_client(fake)
    client.chat(MESSAGES, json_mode=True)
    assert fake.last_kwargs["format"] == "json"
    client.chat(MESSAGES)
    assert fake.last_kwargs["format"] is None


def test_empty_message_list_is_rejected():
    with pytest.raises(ValueError):
        make_client(FakeOllama()).chat([])


@pytest.mark.parametrize(
    "error",
    [
        ollama.ResponseError("model not found"),
        ConnectionError("server down"),
        httpx.ConnectError("refused"),
    ],
)
def test_library_errors_become_llm_unavailable(error):
    with pytest.raises(LlmUnavailableError):
        make_client(FakeOllama(error=error)).chat(MESSAGES)


def test_empty_answer_is_an_error():
    with pytest.raises(LlmUnavailableError):
        make_client(FakeOllama(content="   ")).chat(MESSAGES)
