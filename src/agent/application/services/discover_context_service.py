from agent.application.port.context_discoverer import ContextDiscoverer
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.policy.context_discover_policy import ContextDiscoverPolicy
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult


class DiscoverContextService:
    def __init__(
            self,
            context_discoverer: ContextDiscoverer,
            context_discover_policy: ContextDiscoverPolicy,
            tool_executor: ToolExecutor
    ) -> None:
        self._context_discoverer = context_discoverer
        self._context_discover_policy = context_discover_policy
        self._tool_executor = tool_executor

    def discover(self, discover_result: RequirementAnalysisResult, prompt: Prompt) -> ProjectContext | None:
        if not discover_result.require_context:
            return None

        discover_result = self._context_discoverer.discover(discover_result, prompt, self._tool_executor)
        self._context_discover_policy.evaluate(discover_result).enforce("Discover project context failed")

        return discover_result
