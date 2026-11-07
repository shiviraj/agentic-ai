from agent.application.port.approval_gateway import ApprovalGateway
from agent.application.tool.tool import Tool
from agent.domain.policy.tool_approval_policy import ToolApprovalPolicy
from agent.domain.vo.approval_decision import ApprovalDecision
from agent.domain.vo.tool_result import ToolResult
from agent.shared.logger.logger import Logger


class ToolExecutor:
    def __init__(self, policy: ToolApprovalPolicy, approval_gateway: ApprovalGateway) -> None:
        self._policy = policy
        self._approval_gateway = approval_gateway
        self._logger = Logger("ToolExecutor")
        self._version = 0

    def execute(self, tool: Tool, arguments: dict[str, object]) -> ToolResult:
        decision = self._policy.decide(tool.tool_risk)
        self._logger.debug(
            f"Tool executing started:\n\tTool: {tool.display_name}, arguments: {tool.display_arguments(arguments)}, decision: {decision}"
        )
        if decision == ApprovalDecision.DENY:
            return ToolResult(success=False, error="Tool operation is denied.")

        if decision == ApprovalDecision.REQUIRE_APPROVAL:
            self._version += 1
            approved = self._approval_gateway.request_approval(tool)

            if not approved:
                return ToolResult(success=False, error="User declined tool execution.")

        result = tool.execute(arguments)
        self._logger.debug(f"Tool result:\n\t{result}")
        return result

    @property
    def version(self) -> int:
        return self._version
