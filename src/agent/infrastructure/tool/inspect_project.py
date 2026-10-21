from pathlib import Path
from typing import TypedDict

from agent.domain.vo.tool_result import ToolResult
from agent.application.tool.tool import Tool
from agent.domain.vo.tool_risk import ToolRisk
from agent.infrastructure.tool.util import IGNORED_DIRECTORIES


class InspectProject(Tool):
    @property
    def display_name(self) -> str:
        return "Inspect the current project directory"

    @property
    def name(self) -> str:
        return "inspect_project"

    @property
    def description(self) -> str:
        return "Inspect the current project directory and return its name and top-level file names."

    @property
    def tool_risk(self) -> ToolRisk:
        return ToolRisk.READ_ONLY

    @property
    def parameters_schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def display_arguments(self, arguments: dict[str, object]) -> str | None:
        return None

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        files = sorted(
            str(path.relative_to(self.workspace_root))
            for path in self.workspace_root.rglob("*")
            if path.is_file()
            and not any(
                part in IGNORED_DIRECTORIES
                for part in path.relative_to(self.workspace_root).parts
            )
            and not any(
                part.startswith(".")
                for part in path.relative_to(self.workspace_root).parts
            )
        )

        return ToolResult(success=True, data={"project_directory": self.workspace_root.name, "files": files})
