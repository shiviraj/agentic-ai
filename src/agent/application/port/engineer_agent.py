from abc import abstractmethod

from agent.application.agent.dto.analyze_result import AnalyzeUserRequestResult
from agent.domain.vo.user_request import UserRequest


class EngineerAgent:
    @abstractmethod
    def analyze(self, user_request: UserRequest) -> AnalyzeUserRequestResult: ...
