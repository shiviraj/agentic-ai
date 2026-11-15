from abc import ABC, abstractmethod

from agent.domain.entity.message import Message
from agent.domain.vo.task_analysis import AnalysisResult


class AnalysisAgent(ABC):
    @abstractmethod
    def execute(self, context: tuple[Message, ...]) -> AnalysisResult: ...
