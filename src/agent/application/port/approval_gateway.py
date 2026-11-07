from abc import ABC, abstractmethod

from agent.application.tool.tool import Tool


class ApprovalGateway(ABC):
    @abstractmethod
    def request_approval(self, tool: Tool) -> bool:
        """Return True only when the user explicitly approves."""
