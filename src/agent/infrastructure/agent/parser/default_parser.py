import json
from typing import Any

from agent.domain.errors import InvalidAgentResponseError
from agent.domain.vo.chat_response import ChatResponse
from agent.infrastructure.agent.parser.field_check import require_str
from agent.infrastructure.agent.parser.output_parser import OutputParser


class DefaultParser(OutputParser[ChatResponse]):
    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                },
            },
            "required": ["content"],
            "additionalProperties": False,
        }

    def parse(self, raw: str) -> ChatResponse:
        try:
            data = json.loads(raw)
            content = require_str(data, "content")
            return ChatResponse(content)
        except (json.JSONDecodeError, KeyError, ValueError) as error:
            raise InvalidAgentResponseError(f"Bad LLM output: {raw!r}") from error
