from dataclasses import dataclass


@dataclass(frozen=True)
class ProposedPlanStep:
    title: str
    description: str


