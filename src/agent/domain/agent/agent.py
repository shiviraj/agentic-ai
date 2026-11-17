from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from agent.domain.entity.message import Message
from agent.domain.tool.tool import ToolDefinition
from agent.domain.vo.tool_response import ToolResponse

T = TypeVar("T")


class Agent(ABC, Generic[T]):
    @abstractmethod
    def execute(self, context: tuple[Message, ...]) -> T: ...

    @abstractmethod
    def execute_tools(self, context: tuple[Message, ...], tools: tuple[ToolDefinition, ...]) -> ToolResponse: ...
