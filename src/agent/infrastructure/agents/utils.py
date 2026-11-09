from typing import Any

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
