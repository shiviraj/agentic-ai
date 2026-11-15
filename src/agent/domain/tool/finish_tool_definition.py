from agent.domain.tool.tool import ToolDefinition

FINISH_TOOL_DEFINITION = ToolDefinition(
    provider="__agent__",
    name="finish",
    description="Terminate the current investigation and return its findings. "
    "You MUST call this tool when sufficient information has been "
    "collected or when further tool call is not possible. ",
    input_schema={
        "type": "object",
        "properties": {
            "summary": {"type": "string", "description": "A detailed summary of the investigation."},
        },
        "required": ["summary"],
    },
)
