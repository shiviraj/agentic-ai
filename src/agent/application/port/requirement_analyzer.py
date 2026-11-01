from abc import ABC, abstractmethod

from agent.domain.vo.prompt import Prompt
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult


class RequirementAnalyzer(ABC):

    @abstractmethod
    def analyze(self, prompt: Prompt) -> RequirementAnalysisResult:
        ...
