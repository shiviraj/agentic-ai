from typing import Callable

from agent.application.port.approval_gateway import ApprovalGateway
from agent.domain.policy.tool_approval_policy import ToolApprovalPolicy
from agent.application.tool.tool import Tool
from agent.domain.vo.approval_decision import ApprovalDecision
from agent.domain.vo.tool_result import ToolResult


class ToolExecutor:
    def __init__(
            self,
            policy: ToolApprovalPolicy,
            approval_gateway: ApprovalGateway,
            display_tool_execution: Callable[[Tool, dict[str, object]], None],
            display_tool_result: Callable[[ToolResult], None]
    ) -> None:
        self._policy = policy
        self._approval_gateway = approval_gateway
        self._display_tool_execution = display_tool_execution
        self._display_tool_result = display_tool_result

    def execute(self, tool: Tool, arguments: dict[str, object]) -> ToolResult:
        self._display_tool_execution(tool, arguments)
        decision = self._policy.decide(tool.tool_risk)

        if decision == ApprovalDecision.DENY:
            return ToolResult(success=False, error="Tool operation is denied.")

        if decision == ApprovalDecision.REQUIRE_APPROVAL:
            approved = self._approval_gateway.request_approval(tool)

            if not approved:
                return ToolResult(success=False, error="User declined tool execution.")

        result = tool.execute(arguments)
        self._display_tool_result(result)
        return result
