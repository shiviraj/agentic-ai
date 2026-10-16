ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "requires_context": {
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
    "required": ["requires_context", "context_request"],
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
                "required": ["description"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["steps"],
    "additionalProperties": False,
}
