from typing import Any

from agent.domain.entity.message import Message
from agent.domain.tool.tool import ToolDefinition
from agent.domain.vo.message_type import MessageType


def to_ollama_tools(definitions: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Our ToolDefinition -> the shape Ollama expects in its `tools` argument."""
    return [
        {
            "type": "function",
            "function": {
                "name": f"{definition.provider}::{definition.name}",
                "description": definition.description,
                "parameters": definition.input_schema,
            },
        }
        for definition in definitions
    ]


def to_ollama_payload(messages: list[Message]) -> list[dict]:
    payload = []

    for message in messages:
        if message.message_type == MessageType.AGENT_RESPONSE:
            continue

        item = {
            "role": message.role.value,
            "content": message.content or "",
        }

        if message.message_type == MessageType.TOOL_CALL:
            if not message.tool_calls:
                raise ValueError("TOOL_CALL message must contain at least one tool call")

            item["tool_calls"] = [
                {
                    "function": {
                        "name": f"{tool_call.provider}::{tool_call.name}",
                        "arguments": tool_call.arguments,
                    }
                }
                for tool_call in message.tool_calls
            ]

        elif message.message_type == MessageType.TOOL_RESULT:
            if message.tool is not None:
                item["tool_name"] = f"{message.tool.provider}::{message.tool.name}"

        payload.append(item)

    return payload
