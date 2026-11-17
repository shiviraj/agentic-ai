import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from agent.infrastructure.mcp.tool.command_tool import (
    CommandToolError,
    CommandTools,
)


def create_server(root: Path) -> FastMCP:
    commands = CommandTools(root)
    server = FastMCP("terminal")

    @server.tool
    def run_command(
        arguments: list[str], directory: str = ".", timeout: int = 60, background: bool = False
    ) -> dict[str, object]:
        """Execute an approved command inside the project workspace.

        Arguments must be provided as a list.

        Examples:
        - ["npm", "test"]
        - ["npm", "run", "build"]
        - ["npx", "tsc", "--noEmit"]
        - ["uv", "run", "pytest"]

        Commands are restricted by an allowlist.
        Shell execution is disabled.

        Set background=True for long-running commands.
        Background execution returns a process_id that can be
        used with get_command_status, get_command_output,
        and terminate_command.

        The working directory must be relative to the workspace.
        """
        try:
            return commands.run_command(
                arguments=arguments, directory=directory, timeout=timeout, background=background
            )
        except CommandToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def get_command_status(process_id: str) -> dict[str, object]:
        """Get the execution status of a background command.

        Returns running/completed status and exit code.
        """
        try:
            return commands.get_command_status(process_id)
        except CommandToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def get_command_output(process_id: str) -> dict[str, object]:
        """Retrieve stdout and stderr of a background command.

        Output is limited to the configured maximum size.
        """
        try:
            return commands.get_command_output(process_id)
        except CommandToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def terminate_command(process_id: str) -> dict[str, object]:
        """Terminate a running background command.

        Attempts graceful termination first, followed by
        forced termination if necessary.
        """
        try:
            return commands.terminate_command(process_id)
        except CommandToolError as error:
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
