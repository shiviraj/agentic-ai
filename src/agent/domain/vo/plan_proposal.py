from dataclasses import dataclass


@dataclass(frozen=True)
class ProposedPlanStep:
    title: str
    description: str


@dataclass(frozen=True)
class PlanProposal:
    steps: tuple[ProposedPlanStep, ...]
