import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from agent.infrastructure.mcp.tool.filesystem_tool import (
    FilesystemToolError,
    FilesystemTools,
)


def create_server(root: Path) -> FastMCP:
    files = FilesystemTools(root)
    server = FastMCP("filesystem")

    @server.tool
    def inspect_project(directory: str = ".", max_results: int = 1000) -> dict[str, object]:
        """Inspect project structure recursively.

        Returns project file paths relative to the workspace root.

        Ignored directories such as node_modules, .git, dist,
        build and .venv are excluded.

        Results are limited to max_results.
        """
        try:
            return files.inspect_project(directory=directory, max_results=max_results)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def read_file(path: str) -> dict[str, object]:
        """Read the full text content of a project file.

        The path must be relative to the project root.
        Example: 'package.json' or 'src/index.ts'.

        Binary files and files larger than 200 KB are refused.
        """
        try:
            return files.read_file(path)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def write_file(path: str, content: str, overwrite: bool = False) -> dict[str, object]:
        """Create or overwrite a project file.

        The path must be relative to the project root.
        Existing files require overwrite=True.
        """
        try:
            return files.write_file(path, content, overwrite)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def edit_file(path: str, old_text: str, new_text: str) -> dict[str, object]:
        """Replace an exact, unique text occurrence in a project file."""
        try:
            return files.edit_file(path, old_text, new_text)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def create_directory(path: str) -> dict[str, object]:
        """Create a directory inside the project workspace."""
        try:
            return files.create_directory(path)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def delete_file(path: str) -> dict[str, object]:
        """Delete an existing file from the project.

        Only files can be deleted.
        Directories and protected directories cannot be deleted.
        The path must be relative to the project root.
        """
        try:
            return files.delete_file(path)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def move_file(source: str, destination: str, overwrite: bool = False) -> dict[str, object]:
        """Move or rename a file within the project.

        Both paths must be relative to the project root.
        Destination directories must already exist.
        Existing destination files are not overwritten unless
        overwrite=True is explicitly provided.
        """
        try:
            return files.move_file(source=source, destination=destination, overwrite=overwrite)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def get_file_info(path: str) -> dict[str, object]:
        """Retrieve metadata for a project file or directory.

        Returns name, extension, type, size, and timestamps.
        The path must be relative to the project root.
        """
        try:
            return files.get_file_info(path)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def search_files(
        query: str, directory: str = ".", file_pattern: str = "*", search_content: bool = True, max_results: int = 100
    ) -> dict[str, object]:
        """Search project files by filename and/or file content.

        Search is case-insensitive.

        Examples:
        - Search filenames: query='user_service', search_content=False
        - Search TypeScript files: query='UserService', file_pattern='*.ts'
        - Search Python files: query='class Agent', file_pattern='*.py'

        Ignored directories and oversized or binary files are excluded.
        """
        try:
            return files.search_files(
                query=query,
                directory=directory,
                file_pattern=file_pattern,
                search_content=search_content,
                max_results=max_results,
            )
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    return server


def main() -> None:
    load_dotenv()

    cwd = Path.cwd().resolve()
    workspace = os.getenv("WORKSPACE")

    if not workspace:
        raise RuntimeError("WORKSPACE environment variable is not configured.")

    root = (cwd / workspace).resolve()

    if not root.is_dir():
        raise RuntimeError(f"Workspace directory does not exist: {root}")

    create_server(root).run()


if __name__ == "__main__":
    main()
