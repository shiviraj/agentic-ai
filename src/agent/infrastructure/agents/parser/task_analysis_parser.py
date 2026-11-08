import json

from agent.domain.vo.task_analysis import TaskAnalysis
from agent.infrastructure.agents.field_check import require_str, require_str_list
from agent.infrastructure.agents.parser.output_parser import OutputParser


class TaskAnalysisParser(OutputParser[TaskAnalysis]):
    @property
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "requirements": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary", "requirements"],
        }

    def parse(self, raw: str) -> TaskAnalysis:
        data = json.loads(raw)

        summary = require_str(data, "summary", min_length=5)
        requirements = require_str_list(data, "requirements")

        return TaskAnalysis(summary, requirements)
