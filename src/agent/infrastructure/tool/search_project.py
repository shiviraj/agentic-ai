from pathlib import Path
from typing import TypedDict

from agent.domain.vo.tool_result import ToolResult
from agent.application.tool.tool import Tool
from agent.domain.vo.tool_risk import ToolRisk
from agent.infrastructure.tool.util import MAX_FILE_SIZE_BYTES, IGNORED_DIRECTORIES


class SearchProjectArgs(TypedDict):
    query: str
    file_pattern: str
    max_results: int


class SearchProject(Tool[SearchProjectArgs]):
    """Read a UTF-8 text file from the project workspace."""

    @property
    def display_name(self) -> str:
        return "Search project text"

    @property
    def name(self) -> str:
        return "search_project"

    @property
    def description(self) -> str:
        return "Search project text files for a case-insensitive query. Returns matching file paths, line " \
               "numbers, and line content. Read-only; does not modify files."

    @property
    def tool_risk(self) -> ToolRisk:
        return ToolRisk.READ_ONLY

    @property
    def parameters_schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for.",
                    "minLength": 1,
                },
                "file_pattern": {
                    "type": "string",
                    "description": (
                        "Glob pattern for filenames, such as *.py or *.ts."
                    ),
                    "default": "*",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of matching lines to return.",
                    "minimum": 1,
                    "default": 100,
                },
            },
            "required": ["query", "file_pattern", "max_results"],
            "additionalProperties": False,
        }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def display_arguments(self, arguments: SearchProjectArgs) -> str | None:
        return f"Query: {arguments['query']}, file_pattern: {arguments['file_pattern']}, max_results: {arguments['max_results']}"

    def execute(self, arguments: SearchProjectArgs) -> ToolResult:
        query = arguments["query"]
        file_pattern = arguments["file_pattern"]
        max_results = arguments["max_results"]

        matches: list[dict[str, object]] = []
        files_scanned = 0
        truncated = False

        for path in sorted(self.workspace_root.rglob(file_pattern)):
            relative_path = path.relative_to(self.workspace_root)

            if any(
                    part.startswith(".") or part in IGNORED_DIRECTORIES
                    for part in relative_path.parts[:-1]
            ):
                continue

            if not path.is_file():
                continue

            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            files_scanned += 1

            for line_number, line in enumerate(content.splitlines(), start=1):
                if query.casefold() not in line.casefold():
                    continue

                if len(matches) >= max_results:
                    truncated = True
                    break

                matches.append({"filename": relative_path.as_posix(), "line_number": line_number, "line": line.strip()})

            if truncated:
                break

        return ToolResult(
            success=True,
            data={
                "query": query,
                "file_pattern": file_pattern,
                "files_scanned": files_scanned,
                "match_count": len(matches),
                "truncated": truncated,
                "matches": matches,
            }
        )
