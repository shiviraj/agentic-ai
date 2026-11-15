from abc import ABC, abstractmethod

from agent.domain.entity.message import Message
from agent.domain.tool.tool import ToolDefinition
from agent.domain.vo.tool_response import ToolResponse


class InvestigationAgent(ABC):
    @abstractmethod
    def execute(self, context: tuple[Message, ...], tools: tuple[ToolDefinition, ...]) -> ToolResponse: ...
