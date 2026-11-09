from abc import abstractmethod

from agent.application.service.dto.analyze_user_request_result import AnalyzeUserRequestResult
from agent.domain.aggregate.conversation import Conversation


class EngineerAgent:
    @abstractmethod
    def analyze(self, conversation: Conversation) -> AnalyzeUserRequestResult: ...
