from abc import ABC, abstractmethod

from agent.domain.entity.message import Message
from agent.domain.vo.chat_response import ChatResponse


class ResponseAgent(ABC):
    @abstractmethod
    def execute(self, context: tuple[Message, ...]) -> ChatResponse: ...
