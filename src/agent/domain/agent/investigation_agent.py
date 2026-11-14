from abc import ABC, abstractmethod

from agent.domain.agent.dto.investigation_agent_result import InvestigationAgentResult
from agent.domain.entity.message import Message
from agent.domain.tool.tool import ToolDefinition


class InvestigationAgent(ABC):
    @abstractmethod
    def execute(self, context: list[Message], tools: list[ToolDefinition]) -> InvestigationAgentResult: ...
