from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from agent.domain.llm.message import Message


class LLMClient(ABC):
    """The only thing the app knows about 'the LLM'."""

    @abstractmethod
    def chat(self, messages: Sequence[Message], schema: dict | None = None) -> str:
        """Send the messages, return the model's text answer.

        schema asks the model to answer with valid JSON using schema
        Raises LlmUnavailableError if the model cannot be used.
        """

    @abstractmethod
    def tool(self, messages: Sequence[Message], tools: list[dict[str, Any]]) -> str:
        """Send the messages, return the model's tool calls.

        Raises LlmUnavailableError if the model cannot be used.
        """
