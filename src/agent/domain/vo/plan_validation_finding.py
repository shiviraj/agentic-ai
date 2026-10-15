from dataclasses import dataclass
from enum import StrEnum

from agent.shared.domain.vo import ValueObject


class FindingSeverity(StrEnum):
    ERROR = 'error'
    WARNING = 'warning'


@dataclass(frozen=True, slots=True)
class PlanValidationFinding(ValueObject):
    code: str
    message: str
    severity: FindingSeverity
    step_sequence: int | None = None
