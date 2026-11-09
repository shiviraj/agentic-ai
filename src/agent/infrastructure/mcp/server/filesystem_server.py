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
    def inspect_project(path: str) -> str:
        """Inspect the project structure.

        Recursively lists all project files using paths relative
        to the given path. Skips ignored directories such as
        node_modules, .git, dist and build.

        Use this tool first to discover the project structure.
        """
        try:
            return files.inspect_project(path)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def read_file(path: str) -> str:
        """Read the full text content of a project file.

        The path must be relative to the project root.
        Example: 'package.json' or 'src/index.ts'.

        Binary files and files larger than 200 KB are refused.
        """
        try:
            return files.read_file(path)
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
