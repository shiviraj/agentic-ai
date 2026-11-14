from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from agent.domain.entity.message import Message
from agent.domain.tool.tool import ToolDefinition
from agent.domain.vo.chat_response import ChatResponse
from agent.domain.vo.tool_response import ToolResponse


class LLMClient(ABC):
    """The only thing the app knows about 'the LLM'."""

    @abstractmethod
    def chat(self, messages: Sequence[Message], schema: dict[str, Any] | None = None) -> ChatResponse:
        """Send the messages, return the model's text answer.

        schema asks the model to answer with valid JSON using schema
        Raises LlmUnavailableError if the model cannot be used.
        """

    @abstractmethod
    def tool(self, messages: Sequence[Message], tools: list[ToolDefinition]) -> ToolResponse:
        """Send the messages, return the model's tool calls.

        Raises LlmUnavailableError if the model cannot be used.
        """
