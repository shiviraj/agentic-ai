from dataclasses import dataclass
from datetime import datetime

from agent.domain.tool.tool import ToolCall, ToolResult
from agent.domain.vo.message_id import MessageId
from agent.domain.vo.message_type import MessageType
from agent.domain.vo.role import Role
from agent.shared.domain.aggregate import Aggregate


@dataclass
class Message(Aggregate[MessageId]):
    role: Role
    message_type: MessageType
    content: str | None
    created_at: datetime

    agent_name: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    tool: ToolCall | None = None

    @classmethod
    def create_text(cls, role: Role, content: str | None) -> "Message":
        return Message.create(role=role, content=content, message_type=MessageType.TEXT)

    @classmethod
    def create_tools(cls, tools: tuple[ToolCall, ...]) -> "Message":
        return Message.create(role=Role.ASSISTANT, content="", message_type=MessageType.TOOL_CALL, tool_calls=tools)

    @classmethod
    def create_tool_result(cls, tool: ToolCall, tool_result: ToolResult) -> "Message":
        return Message.create(role=Role.TOOL, content=str(tool_result), tool=tool, message_type=MessageType.TOOL_RESULT)

    @classmethod
    def create(
        cls,
        role: Role,
        message_type: MessageType,
        content: str | None,
        agent_name: str | None = None,
        tool_calls: tuple[ToolCall, ...] = (),
        tool: ToolCall | None = None,
    ) -> "Message":
        return cls(
            id=MessageId.generate(),
            role=role,
            message_type=message_type,
            content=content,
            created_at=datetime.now(),
            agent_name=agent_name,
            tool_calls=tool_calls,
            tool=tool,
        )
