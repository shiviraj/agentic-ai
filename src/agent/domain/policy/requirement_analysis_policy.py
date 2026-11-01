from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult
from agent.shared.domain.policy.policy import Policy
from agent.shared.domain.policy.policy_result import PolicyResult


class RequirementAnalysisPolicy(Policy[RequirementAnalysisResult]):
    def evaluate(self, data: RequirementAnalysisResult) -> PolicyResult:
        errors = []
        if not isinstance(data, RequirementAnalysisResult):
            errors.append("Analysis response must be a RequirementAnalysisResult object.")

        if not isinstance(data.require_context, bool):
            errors.append("require_context must be a boolean.")

        if not isinstance(data.context_request, str):
            errors.append("context_request must be a string.")

        return PolicyResult.create(errors)
