from abc import ABC, abstractmethod

from agent.application.services.tool_executor import ToolExecutor
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult


class ContextDiscoverer(ABC):

    @abstractmethod
    def discover(
            self,
            analysis_result: RequirementAnalysisResult,
            prompt: Prompt,
            tool_executor: ToolExecutor
    ) -> ProjectContext:
        ...
