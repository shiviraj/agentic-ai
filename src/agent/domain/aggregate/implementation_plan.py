from dataclasses import dataclass

from agent.domain.entity.plan_step import PlanStep, TaskStatus
from agent.domain.vo.plan_id import PlanId
from agent.shared.domain.aggregate import Aggregate


@dataclass(eq=False)
class ImplementationPlan(Aggregate[PlanId]):
    steps: list[PlanStep]
    status: TaskStatus = TaskStatus.DRAFT
