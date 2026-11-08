from dataclasses import dataclass
from enum import Enum


class ResultStatus(str, Enum):
    DONE = "DONE"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class AgentResult:
    status: ResultStatus
    output: str

    @classmethod
    def done(cls, output: str) -> "AgentResult":
        return cls(status=ResultStatus.DONE, output=output)

    @classmethod
    def failed(cls, reason: str) -> "AgentResult":
        return cls(status=ResultStatus.FAILED, output=reason)

    @classmethod
    def rejected(cls, feedback: str) -> "AgentResult":
        """Work was done but is not good enough; feedback says what to fix."""
        return cls(status=ResultStatus.REJECTED, output=feedback)
