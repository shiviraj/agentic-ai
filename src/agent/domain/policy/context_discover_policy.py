from agent.domain.vo.project_context import ProjectContext
from agent.shared.domain.policy.policy import Policy
from agent.shared.domain.policy.policy_result import PolicyResult


class ContextDiscoverPolicy(Policy[ProjectContext]):
    def evaluate(self, data: ProjectContext) -> PolicyResult:
        errors = []
        if not isinstance(data, ProjectContext):
            errors.append("Analysis response must be a ProjectContext object.")

        # if not isinstance(data.require_context, bool):
        #     errors.append("require_context must be a boolean.")

        # if not isinstance(data.context_request, str):
        #     errors.append("context_request must be a string.")

        return PolicyResult.create(errors)
