from agent.domain.vo.task_analysis import OpenQuestionCategory, TaskAnalysis, TaskAnalysisStatus
from agent.shared.domain.policy.policy import Policy
from agent.shared.domain.policy.policy_result import PolicyResult


class TaskAnalysisPolicy(Policy[TaskAnalysis]):
    def evaluate(self, data: TaskAnalysis) -> PolicyResult:
        errors = []
        if data.status == TaskAnalysisStatus.READY and data.open_questions:
            errors.append(f"{TaskAnalysisStatus.READY.value} state should not contain any open questions")

        if data.status == TaskAnalysisStatus.NEEDS_CLARIFICATION and any(
            question.category == OpenQuestionCategory.CODEBASE_CONTEXT for question in data.open_questions
        ):
            errors.append(
                f"{TaskAnalysisStatus.NEEDS_CLARIFICATION.value} state should not contain open questions"
                "of {OpenQuestionCategory.CODEBASE_CONTEXT.value}"
            )

        if data.status == TaskAnalysisStatus.NEEDS_INVESTIGATION and any(
            question.category == OpenQuestionCategory.USER_CLARIFICATION for question in data.open_questions
        ):
            errors.append(
                f"{TaskAnalysisStatus.NEEDS_INVESTIGATION.value} state should not contain open questions"
                "of {OpenQuestionCategory.USER_CLARIFICATION.value}"
            )
        return PolicyResult.create(errors=errors)
