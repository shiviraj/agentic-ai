from agent.domain.tool.tool import ToolDefinition

FINISH_TOOL_DEFINITION = ToolDefinition(
    provider="__agent__",
    name="finish",
    description="Terminate the current investigation and return its findings. "
    "You MUST call this tool when sufficient information has been "
    "collected or when further investigation is not possible. "
    "Do not return a normal text response.",
    input_schema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["completed", "partial", "failed"],
                "description": "Investigation completion status.",
            },
            "content": {"type": "string", "description": "A detailed summary of the investigation."},
        },
        "required": [
            "status",
            "content",
        ],
    },
)
