import json
from typing import Any

from agent.application.service.dto.analyze_user_request_result import AnalyzeUserRequestResult, RequestCategory
from agent.domain.errors import InvalidAgentOutputError
from agent.infrastructure.agents.field_check import require_str
from agent.infrastructure.agents.parser.output_parser import OutputParser


class AnalyzeUserRequestParser(OutputParser[AnalyzeUserRequestResult]):
    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [c.value for c in RequestCategory],
                },
                "response": {"type": "string", "minLength": 10},
            },
            "required": ["category", "response"],
            "additionalProperties": False,
        }

    def parse(self, raw: str) -> AnalyzeUserRequestResult:
        try:
            data = json.loads(raw)
            category = require_str(data, "category")
            response = require_str(data, "response", min_length=10)
            return AnalyzeUserRequestResult(category=RequestCategory(category), response=response)
        except (json.JSONDecodeError, KeyError, ValueError) as error:
            raise InvalidAgentOutputError(f"Bad LLM output: {raw!r}") from error
