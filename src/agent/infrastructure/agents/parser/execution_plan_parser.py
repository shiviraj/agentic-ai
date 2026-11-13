import json
from typing import Any

from agent.domain.aggregate.execution_plan import ExecutionAgent, ExecutionPlan, ExecutionStep
from agent.domain.errors import InvalidAgentOutputError
from agent.infrastructure.agents.field_check import require_str
from agent.infrastructure.agents.parser.output_parser import OutputParser


class ExecutionPlanParser(OutputParser[ExecutionPlan]):
    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "agent": {"type": "string", "enum": [e.value for e in ExecutionAgent]},
                        },
                        "required": ["title", "description", "agent"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                }
            },
            "required": ["steps"],
            "additionalProperties": False,
        }

    def parse(self, raw: str) -> ExecutionPlan:
        try:
            data = json.loads(raw)
            steps = tuple(self._parse_execution_step(step, index) for index, step in enumerate(data["steps"]))

            return ExecutionPlan.create(steps=steps)

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise InvalidAgentOutputError(f"Bad LLM output: {raw!r}") from error

    def _parse_execution_step(self, data: Any, index: int) -> ExecutionStep:
        if not isinstance(data, dict):
            raise ValueError("Each step must be an object.")

        return ExecutionStep(
            sequence=index,
            title=require_str(data, "title"),
            description=require_str(data, "description"),
            agent=ExecutionAgent(require_str(data, "agent")),
        )
