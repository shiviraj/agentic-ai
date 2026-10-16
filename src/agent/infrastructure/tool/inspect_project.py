from pathlib import Path

from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.tool.tool import Tool
from agent.infrastructure.tool.util import IGNORED_DIRECTORIES


class InspectProject(Tool):
    name: str = "inspect_project"
    description: str = "Inspect the current project directory and return its name and top-level file names."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        files = sorted(
            path.name
            for path in self.workspace_root.iterdir()
            if path.name not in IGNORED_DIRECTORIES and not path.name.startswith(".")
        )

        return ToolResult(
            success=True,
            data={"project_directory": self.workspace_root.name, "files": files}
        )
