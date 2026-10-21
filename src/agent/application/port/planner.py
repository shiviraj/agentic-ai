from abc import abstractmethod, ABC

from agent.application.services.tool_executor import ToolExecutor
from agent.domain.vo.plan_proposal import RequirementAnalysisResult, ProposedPlanStep
from agent.domain.vo.prompt import Prompt


class Planner(ABC):
    """Application port for generating implementation plans."""

    @abstractmethod
    def analyze_requirement(self, prompt: Prompt) -> RequirementAnalysisResult:
        ...

    @abstractmethod
    def discover_context(
            self,
            analysis_result: RequirementAnalysisResult,
            prompt: Prompt,
            tool_executor: ToolExecutor
    ) -> str | None:
        ...

    @abstractmethod
    def summarize_context(self, context: str, prompt: Prompt) -> str:
        ...

    @abstractmethod
    def create_proposal(self, context: str | None, prompt: Prompt) -> list[ProposedPlanStep]:
        ...
