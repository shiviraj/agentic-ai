from collections.abc import Sequence

from agent.application.port.llm_client import LLMClient
from agent.domain.llm.message import Message


class FakeLLMClient(LLMClient):
    """Returns pre-written answers, in order, and records what it was sent."""

    def __init__(self, replies: list[str]) -> None:
        self._replies = list(replies)
        self.calls: list[list[Message]] = []
        self.json_modes: list[bool] = []

    def chat(self, messages: Sequence[Message], json_mode: bool = False) -> str:
        self.calls.append(list(messages))
        self.json_modes.append(json_mode)
        if not self._replies:
            raise AssertionError("FakeLlmClient ran out of replies")
        return self._replies.pop(0)
