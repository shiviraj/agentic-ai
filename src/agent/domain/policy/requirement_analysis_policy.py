from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult
from agent.shared.domain.policy.policy import Policy
from agent.shared.domain.policy.policy_result import PolicyResult


class RequirementAnalysisPolicy(Policy[RequirementAnalysisResult]):
    def evaluate(self, data: RequirementAnalysisResult) -> PolicyResult:
        errors = []

        return PolicyResult.create(errors)
