from abc import ABC, abstractmethod

from agent.domain.agent.dto.engineer_agent_result import EngineerAgentResult
from agent.domain.entity.message import Message


class EngineerAgent(ABC):
    @abstractmethod
    def execute(self, context: tuple[Message, ...]) -> EngineerAgentResult: ...
