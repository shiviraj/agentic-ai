from pathlib import Path

from agent.infrastructure.tool.create_project_file import CreateProjectFile
from agent.infrastructure.tool.edit_project_file import EditProjectFile
from agent.infrastructure.tool.inspect_project import InspectProject
from agent.infrastructure.tool.list_project_files import ListProjectFiles
from agent.infrastructure.tool.read_project_file import ReadProjectFile
from agent.infrastructure.tool.run_project_command import RunProjectCommand
from agent.infrastructure.tool.search_project import SearchProject
from agent.infrastructure.tool_registry import ToolRegistry


def create_tool_registry(workspace_root: Path) -> ToolRegistry:
    if not workspace_root.resolve().is_dir():
        raise NotADirectoryError(f"Project workspace is not a directory: {workspace_root.resolve().name}")

    create_project_file = CreateProjectFile(workspace_root)
    edit_project_file = EditProjectFile(workspace_root)
    inspect_project = InspectProject(workspace_root)
    list_project_files = ListProjectFiles(workspace_root)
    read_project_file = ReadProjectFile(workspace_root)
    search_project = SearchProject(workspace_root)
    run_project_command = RunProjectCommand(workspace_root)

    all_tools = [
        create_project_file,
        edit_project_file,
        inspect_project,
        list_project_files,
        read_project_file,
        run_project_command,
        search_project,
    ]
    discovery_tools = [
        inspect_project,
        list_project_files,
        read_project_file,
        # run_project_command,
        search_project
    ]
    return ToolRegistry(tools=all_tools, discovery_tools=discovery_tools)
