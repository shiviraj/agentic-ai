import json
from typing import Any

from agent.domain.agent.dto.engineer_agent_result import EngineerAgentResult, RequestType
from agent.domain.errors import InvalidAgentResponseError
from agent.infrastructure.agent.parser.field_check import require_str
from agent.infrastructure.agent.parser.output_parser import OutputParser


class EngineerAgentResultParser(OutputParser[EngineerAgentResult]):
    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "request_type": {
                    "type": "string",
                    "enum": [c.value for c in RequestType],
                },
                "summary": {"type": "string", "minLength": 10},
            },
            "required": ["request_type", "summary"],
            "additionalProperties": False,
        }

    def parse(self, raw: str) -> EngineerAgentResult:
        try:
            data = json.loads(raw)
            request_type = require_str(data, "request_type")
            summary = require_str(data, "summary")
            return EngineerAgentResult(request_type=RequestType(request_type), summary=summary)
        except (json.JSONDecodeError, KeyError, ValueError) as error:
            raise InvalidAgentResponseError(f"Bad LLM output: {raw!r}") from error
