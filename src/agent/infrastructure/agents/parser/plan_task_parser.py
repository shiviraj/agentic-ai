import json
from typing import Any

from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.entity.plan_step import PlanStep
from agent.domain.errors import InvalidAgentOutputError
from agent.domain.vo.plan_id import PlanId
from agent.infrastructure.agents.field_check import require_str
from agent.infrastructure.agents.parser.output_parser import OutputParser


class PlanTaskParser(OutputParser[ImplementationPlan]):
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
                        },
                        "required": ["title", "description"],
                    },
                },
            },
            "required": ["steps"],
        }

    def parse(self, raw: str) -> ImplementationPlan:
        try:
            data = json.loads(raw)
            steps = data.get("steps")
            if not isinstance(steps, list):
                raise ValueError("'steps' must be an array.")
            sub_tasks = tuple(self._parse_step(sequence, step) for sequence, step in enumerate(steps, start=1))

            return ImplementationPlan(id=PlanId.generate(), steps=sub_tasks)

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise InvalidAgentOutputError(f"Bad LLM output: {raw!r}") from error

    def _parse_step(self, sequence: int, data: Any) -> PlanStep:
        if not isinstance(data, dict):
            raise ValueError("Each sub task must be an object.")

        return PlanStep.create(
            sequence=sequence,
            title=require_str(data, "title"),
            description=require_str(data, "description"),
        )
