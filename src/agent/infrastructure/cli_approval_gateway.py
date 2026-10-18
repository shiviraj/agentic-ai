from prompt_toolkit import prompt, HTML
from rich.console import Console

from agent.application.port.approval_gateway import ApprovalGateway
from agent.application.tool.tool import Tool


class CliApprovalGateway(ApprovalGateway):

    def __init__(self, console: Console) -> None:
        self._console = console

    def request_approval(self, tool: Tool) -> bool:
        # self._console.print("[bold yellow]Approval required: [/bold yellow]Allow this operation? [y/N]: ")
        # self._console.print(f"Tool: {tool.display_name}\tRisk: {tool.tool_risk}")
        # self._console.print(f"Arguments: {arguments}")

        answer = prompt(HTML("<ansiyellow><bold>Allow this operation? [y/N]: </bold></ansiyellow>")).strip().lower()
        return answer == "y"
