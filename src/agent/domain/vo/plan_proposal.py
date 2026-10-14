from dataclasses import dataclass


@dataclass(frozen=True)
class ProposedPlanStep:
    description: str


@dataclass(frozen=True)
class PlanProposal:
    steps: tuple[ProposedPlanStep, ...]
