from dataclasses import dataclass


@dataclass(frozen=True)
class RequirementAnalysisResult:
    require_context: bool
    context_request: str
