from dataclasses import dataclass

from agent.domain.vo.plan_validation_finding import PlanValidationFinding, FindingSeverity
from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True, slots=True)
class ValidationResult(ValueObject):
    findings: tuple[PlanValidationFinding, ...] = ()
    is_valid: bool = True

    @classmethod
    def valid(cls) -> 'ValidationResult':
        return cls()

    @classmethod
    def invalid(cls, *findings: PlanValidationFinding) -> 'ValidationResult':
        return cls(findings=tuple(findings), is_valid=False)

    @classmethod
    def create(cls, issue: tuple[PlanValidationFinding, ...]) -> 'ValidationResult':
        return cls.valid()
