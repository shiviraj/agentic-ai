from dataclasses import dataclass
from enum import Enum


class AnalysisStatus(str, Enum):
    READY = "READY"
    NEEDS_INVESTIGATION = "NEEDS_INVESTIGATION"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    FAILED = "FAILED"


class OpenQuestionCategory(str, Enum):
    CODEBASE_CONTEXT = "CODEBASE_CONTEXT"
    USER_CLARIFICATION = "USER_CLARIFICATION"


class QuestionPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class OpenQuestion:
    question: str
    category: OpenQuestionCategory
    priority: QuestionPriority
    reason: str


@dataclass(frozen=True)
class AnalysisResult:
    status: AnalysisStatus
    summary: str
    expected_outcome: str
    open_questions: list[OpenQuestion]

    def __post_init__(self) -> None:
        errors = []
        if self.status == AnalysisStatus.READY and self.open_questions:
            errors.append(f"{AnalysisStatus.READY.value} state should not contain any open questions")

        if self.status == AnalysisStatus.NEEDS_CLARIFICATION and any(
            question.category == OpenQuestionCategory.CODEBASE_CONTEXT for question in self.open_questions
        ):
            errors.append(
                f"{AnalysisStatus.NEEDS_CLARIFICATION.value} state should not contain open questions"
                "of {OpenQuestionCategory.CODEBASE_CONTEXT.value}"
            )

        if self.status == AnalysisStatus.NEEDS_INVESTIGATION and any(
            question.category == OpenQuestionCategory.USER_CLARIFICATION for question in self.open_questions
        ):
            errors.append(
                f"{AnalysisStatus.NEEDS_INVESTIGATION.value} state should not contain open questions"
                "of {OpenQuestionCategory.USER_CLARIFICATION.value}"
            )
        if errors:
            raise ValueError(errors)
