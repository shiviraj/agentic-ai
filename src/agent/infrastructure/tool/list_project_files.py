from pathlib import Path

from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.tool.tool import Tool
from agent.infrastructure.tool.util import IGNORED_DIRECTORIES


class ListProjectFiles(Tool):
    name: str = "list_project_files"
    description: str = "List project files recursively using paths relative to the project root. Excludes hidden and " \
                       "generated directories. This tool is read-only."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        files: list[str] = []
        for path in sorted(self.workspace_root.rglob("*")):
            relative_path = path.relative_to(self.workspace_root)

            # Skip hidden and generated directories.
            if any(
                    part in IGNORED_DIRECTORIES or part.startswith(".")
                    for part in relative_path.parts[:-1]
            ):
                continue

            if path.is_file():
                files.append(relative_path.as_posix())

        return ToolResult(
            success=True,
            data={"project_directory": self.workspace_root.name, "file_count": len(files), "files": files}
        )
