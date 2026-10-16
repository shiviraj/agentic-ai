from pathlib import Path

from agent.infrastructure.tool.create_project_file import CreateProjectFile
from agent.infrastructure.tool.edit_project_file import EditProjectFile
from agent.infrastructure.tool.inspect_project import InspectProject
from agent.infrastructure.tool.list_project_files import ListProjectFiles
from agent.infrastructure.tool.read_project_file import ReadProjectFile
from agent.infrastructure.tool.search_project import SearchProject
from agent.infrastructure.tool_registry import ToolRegistry


def create_tool_registry(workspace_root: Path) -> ToolRegistry:
    if not workspace_root.resolve().is_dir():
        raise NotADirectoryError(f"Project workspace is not a directory: {workspace_root.resolve().name}")

    return ToolRegistry(
        tools=[
            CreateProjectFile(workspace_root),
            EditProjectFile(workspace_root),
            InspectProject(workspace_root),
            ListProjectFiles(workspace_root),
            ReadProjectFile(workspace_root),
            SearchProject(workspace_root),

        ]
    )
