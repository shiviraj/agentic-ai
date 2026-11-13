from dataclasses import dataclass
from enum import Enum

from agent.domain.vo.plan_id import PlanId
from agent.shared.domain.aggregate import Aggregate


class ExecutionAgent(str, Enum):
    TEST_DESIGN = "TEST_DESIGN"
    IMPLEMENTATION = "IMPLEMENTATION"
    TEST_VERIFICATION = "TEST_VERIFICATION"


@dataclass(frozen=True)
class ExecutionStep:
    sequence: int
    title: str
    description: str
    agent: ExecutionAgent


@dataclass(eq=False)
class ExecutionPlan(Aggregate[PlanId]):
    steps: tuple[ExecutionStep, ...]

    @classmethod
    def create(cls, steps: tuple[ExecutionStep, ...]) -> "ExecutionPlan":
        return cls(id=PlanId.generate(), steps=steps)
