from enum import StrEnum


class ToolRisk(StrEnum):
    READ_ONLY = "READ_ONLY"
    VALIDATION = "VALIDATION"
    MUTATING = "MUTATING"
    DESTRUCTIVE = "DESTRUCTIVE"
    EXTERNAL = "EXTERNAL"
