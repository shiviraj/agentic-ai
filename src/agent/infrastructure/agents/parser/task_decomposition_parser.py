import json
from typing import Any

from agent.domain.aggregate.task import Task
from agent.domain.entity.subtask import Subtask
from agent.domain.errors import InvalidAgentOutputError
from agent.infrastructure.agents.field_check import require_str
from agent.infrastructure.agents.parser.output_parser import OutputParser


class TaskDecompositionParser(OutputParser[Task]):
    @property
    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "subtasks": {
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
            "required": ["title", "description", "subtasks"],
        }

    def parse(self, raw: str) -> Task:
        try:
            data = json.loads(raw)
            subtasks = data.get("subtasks")
            title = require_str(data, "title")
            description = require_str(data, "description")
            if not isinstance(subtasks, list):
                raise ValueError("'subtasks' must be an array.")
            sub_tasks = tuple(
                self._parse_subtask(sequence, subtask) for sequence, subtask in enumerate(subtasks, start=1)
            )

            return Task.create(sub_tasks=sub_tasks, title=title, description=description)

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise InvalidAgentOutputError(f"Bad LLM output: {raw!r}") from error

    def _parse_subtask(self, sequence: int, data: Any) -> Subtask:
        if not isinstance(data, dict):
            raise ValueError("Each sub task must be an object.")

        return Subtask.create(
            sequence=sequence,
            title=require_str(data, "title"),
            description=require_str(data, "description"),
        )
