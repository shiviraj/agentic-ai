from abc import abstractmethod

from agent.application.port.dto.llm_response import ChatResponse
from agent.domain.aggregate.conversation import Conversation


class SummaryAgent:
    @abstractmethod
    def run(self, conversation: Conversation) -> ChatResponse: ...
