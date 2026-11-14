from abc import ABC, abstractmethod

from agent.domain.entity.message import Message
from agent.domain.vo.chat_response import ChatResponse


class ConversationAgent(ABC):
    @abstractmethod
    def execute(self, context: list[Message]) -> ChatResponse: ...
