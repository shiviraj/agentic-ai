from agent.domain.vo.approval_decision import ApprovalDecision
from agent.domain.vo.tool_risk import ToolRisk


class ToolApprovalPolicy:
    """Determines whether an operation requires user approval."""

    def decide(self, risk: ToolRisk) -> ApprovalDecision:
        match risk:
            case ToolRisk.READ_ONLY:
                return ApprovalDecision.ALLOW

            case ToolRisk.VALIDATION:
                return ApprovalDecision.ALLOW

            case ToolRisk.MUTATING:
                return ApprovalDecision.REQUIRE_APPROVAL

            case ToolRisk.DESTRUCTIVE:
                return ApprovalDecision.REQUIRE_APPROVAL

            case ToolRisk.EXTERNAL:
                return ApprovalDecision.REQUIRE_APPROVAL
