from typing import Protocol

from agent.domain.vo.plan_proposal import PlanProposal
from agent.domain.vo.prompt import Prompt


class Planner(Protocol):
    """Application port for generating implementation plans."""

    def generate_plan(self, prompt: Prompt) -> PlanProposal:
        ...
