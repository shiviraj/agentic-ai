from typing import Any

from agent.domain.llm.message import Message
from agent.domain.tool.tool import ToolDefinition


def to_ollama_tools(definitions: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Our ToolDefinition -> the shape Ollama expects in its `tools` argument."""
    return [
        {
            "type": "function",
            "function": {
                "name": definition.name,
                "description": definition.description,
                "parameters": definition.input_schema,
            },
        }
        for definition in definitions
    ]


def to_ollama_payload(messages: list[Message]) -> list[dict]:
    payload = []

    for message in messages:
        item = {
            "role": message.role.value,
            "content": message.content,
        }

        if message.tool_name is not None:
            item["tool_name"] = message.tool_name

        if message.tool_calls is not None:
            item["tool_calls"] = [
                {
                    "function": {
                        "name": tool_call.name,
                        "arguments": tool_call.arguments,
                    }
                }
                for tool_call in message.tool_calls
            ]

        payload.append(item)
    return payload
