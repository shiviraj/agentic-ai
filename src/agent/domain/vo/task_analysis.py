from dataclasses import dataclass
from enum import Enum


class TaskAnalysisStatus(str, Enum):
    READY = "READY"
    NEEDS_INVESTIGATION = "NEEDS_INVESTIGATION"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"


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
class TaskAnalysis:
    status: TaskAnalysisStatus
    task_summary: str
    expected_outcome: str
    open_questions: tuple[OpenQuestion, ...]
