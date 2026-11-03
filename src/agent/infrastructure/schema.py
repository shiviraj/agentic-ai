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
                    "title": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "description": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
                "required": ["title", "description"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["steps"],
    "additionalProperties": False,
}

SUMMARIZE_DISCOVERY_CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
        },
        "project_structure": {
            "type": "array",
            "items": {"type": "string"},
        },
        "framework_and_dependencies": {
            "type": "array",
            "items": {"type": "string"},
        },
        "architecture_and_conventions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "relevant_files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "purpose": {"type": "string"},
                    "evidence": {"type": "string"},
                },
                "required": ["path", "purpose", "evidence"],
                "additionalProperties": False,
            },
        },
        "existing_implementation": {
            "type": "array",
            "items": {"type": "string"},
        },
        "testing_setup": {
            "type": "array",
            "items": {"type": "string"},
        },
        "validation_commands": {
            "type": "array",
            "items": {"type": "string"},
        },
        "implementation_constraints": {
            "type": "array",
            "items": {"type": "string"},
        },
        "missing_information": {
            "type": "array",
            "items": {"type": "string"},
        },
        "uncertainties": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "summary",
        "project_structure",
        "framework_and_dependencies",
        "architecture_and_conventions",
        "relevant_files",
        "existing_implementation",
        "testing_setup",
        "validation_commands",
        "implementation_constraints",
        "missing_information",
        "uncertainties",
    ],
    "additionalProperties": False,
}

FINISH_DISCOVERY_EXECUTION = {
    "type": "function",
    "function": {
        "name": "finish_discovery",
        "description": "Declare project discovery complete when sufficient project context has been gathered to "
                       "create a safe, task-specific implementation plan.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Explain why the gathered project context is sufficient for planning.",
                },
            },
            "required": ["reason"],
            "additionalProperties": False,
        },
    },
}

FINISH_STEP_EXECUTION = {
    "type": "function",
    "function": {
        "name": "finish_step",
        "description": (
            "Terminate the current implementation step after all required "
            "work has been attempted. Report the actual outcome based on "
            "tool results. This must be the final tool call for the step. "
            "Never report success unless the required work and validations "
            "have actually succeeded."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["success", "failure", "blocked"],
                    "description": "Actual outcome of the current step.",
                },
                "summary": {
                    "type": "string",
                    "description": "Summary of work completed or why it stopped.",
                },
            },
            "required": [
                "status",
                "summary",
            ],
            "additionalProperties": False,
        },
    },
}
