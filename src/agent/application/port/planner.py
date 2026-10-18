from agent.application.services.tool_executor import ToolExecutor
from agent.domain.vo.plan_proposal import RequirementAnalysisResult, ProposedPlanStep
from agent.domain.vo.prompt import Prompt


class Planner:
    """Application port for generating implementation plans."""

    def analyze_requirement(self, prompt: Prompt) -> RequirementAnalysisResult:
        ...

    def discover_context(
            self,
            analysis_result: RequirementAnalysisResult,
            prompt: Prompt,
            tool_executor: ToolExecutor
    ) -> str | None:
        ...

    def create_proposal(self, context: str | None, prompt: Prompt) -> list[ProposedPlanStep]:
        ...
