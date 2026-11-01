from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProjectFile:
    path: str
    purpose: str
    relevant_content: str | None = None


@dataclass(frozen=True)
class ProjectContext:
    files: list[ProjectFile] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    conventions: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
