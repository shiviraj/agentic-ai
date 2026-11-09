from agent.application.port.context_discoverer import ContextDiscoverer
from agent.application.service.tool_executor import ToolExecutor
from agent.domain.policy.context_discover_policy import ContextDiscoverPolicy
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult
from agent.domain.vo.user_request import Prompt
from agent.shared.logger.logger import Logger


class DiscoverContextService:
    def __init__(
        self,
        context_discoverer: ContextDiscoverer,
        context_discover_policy: ContextDiscoverPolicy,
        tool_executor: ToolExecutor,
    ) -> None:
        self._context_discoverer = context_discoverer
        self._context_discover_policy = context_discover_policy
        self._tool_executor = tool_executor
        self._logger = Logger("DiscoverContextService")

    def discover(self, discover_result: RequirementAnalysisResult, prompt: Prompt) -> ProjectContext | None:
        if not discover_result.require_context:
            self._logger.debug("Discover project context is not required")
            return None

        self._logger.debug("Discovering project context started")
        discover_result = self._context_discoverer.discover(discover_result, prompt, self._tool_executor)
        self._context_discover_policy.evaluate(discover_result).enforce("Discover project context failed")
        self._logger.debug(f"Discovering result: {discover_result}")
        self._logger.info("Successfully Discovered context", "green bold")
        return discover_result
