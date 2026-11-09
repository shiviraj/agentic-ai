from abc import ABC, abstractmethod

from agent.application.service.tool_executor import ToolExecutor
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult
from agent.domain.vo.user_request import Prompt


class ContextDiscoverer(ABC):
    @abstractmethod
    def discover(
        self, analysis_result: RequirementAnalysisResult, prompt: Prompt, tool_executor: ToolExecutor
    ) -> ProjectContext: ...
