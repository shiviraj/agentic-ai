import json
from typing import Any

from agent.domain.errors import InvalidAgentResponseError
from agent.domain.vo.task_analysis import (
    AnalysisResult,
    AnalysisStatus,
    OpenQuestion,
    OpenQuestionCategory,
    QuestionPriority,
)
from agent.infrastructure.agent.parser.field_check import require_str
from agent.infrastructure.agent.parser.output_parser import OutputParser


class AnalysisResultParser(OutputParser[AnalysisResult]):
    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "expected_outcome": {"type": "string"},
                "open_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "category": {"type": "string", "enum": [e.value for e in OpenQuestionCategory]},
                            "priority": {"type": "string", "enum": [e.value for e in QuestionPriority]},
                            "reason": {"type": "string"},
                        },
                        "required": ["question", "category", "priority", "reason"],
                    },
                },
                "status": {
                    "type": "string",
                    "enum": [e.value for e in AnalysisStatus],
                },
            },
            "required": ["summary", "expected_outcome", "open_questions", "status"],
        }

    def parse(self, raw: str) -> AnalysisResult:
        try:
            data = json.loads(raw)
            status = AnalysisStatus(require_str(data, "status"))
            summary = require_str(data, "summary", min_length=10)
            expected_outcome = require_str(data, "expected_outcome", min_length=10)
            raw_questions = data.get("open_questions")
            if not isinstance(raw_questions, list):
                raise ValueError("'open_questions' must be an array.")
            open_questions = [self._parse_open_question(question) for question in raw_questions]

            return AnalysisResult(
                status=status,
                summary=summary,
                expected_outcome=expected_outcome,
                open_questions=open_questions,
            )

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise InvalidAgentResponseError(f"Bad LLM output: {raw!r}") from error

    def _parse_open_question(self, data: Any) -> OpenQuestion:
        if not isinstance(data, dict):
            raise ValueError("Each open question must be an object.")

        return OpenQuestion(
            question=require_str(data, "question", min_length=5),
            category=OpenQuestionCategory(require_str(data, "category")),
            priority=QuestionPriority(require_str(data, "priority")),
            reason=require_str(data, "reason", min_length=5),
        )
