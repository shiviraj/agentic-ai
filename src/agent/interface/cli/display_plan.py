from rich.console import Console

from agent.application.tool.tool import Tool
from agent.domain.vo.tool_result import ToolResult

def display_tool_result(tool_result: ToolResult) -> None:
    console = Console()
    if tool_result.success:
        console.print(f"[green]Tool executed successfully\tdata: {tool_result.data}[/green]")
    else:
        console.print(f"[red]Failed to execute tool\tError: {tool_result.error}[/red]")


def display_tool_execution(tool: Tool, arguments: dict[str, object]) -> None:
    console = Console()
    console.print(f"Tool execution started")
    console.print(f"Tool: {tool.display_name} \tRisk: {tool.tool_risk}")
    arguments_display_text = tool.display_arguments(arguments)
    if arguments_display_text:
        console.print(f"\tArguments: {arguments_display_text}")

