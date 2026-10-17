ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "require_context": {
            "type": "boolean",
            "description": "Whether understanding the existing project is necessary to create a correct implementation "
                           "plan.",
        },
        "context_request": {
            "type": "string",
            "description": "What project information should be inspected. Use an empty string when context is not "
                           "required."
        },
    },
    "required": ["require_context", "context_request"],
    "additionalProperties": False,
}

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["description", "title"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["steps"],
    "additionalProperties": False,
}
