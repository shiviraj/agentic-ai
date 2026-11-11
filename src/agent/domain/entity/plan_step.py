from dataclasses import dataclass
from enum import Enum

from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.final_response import FinalResponse
from agent.domain.vo.step_id import StepId
from agent.shared.domain.entity import Entity


class TaskStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass(eq=False)
class PlanStep(Entity[StepId]):
    sequence: int
    title: str
    description: str
    status: TaskStatus
    response: FinalResponse | None
    agent_responses: list[AgentResponse]

    @classmethod
    def create(cls, sequence: int, title: str, description: str) -> "PlanStep":
        return cls(
            id=StepId.generate(),
            sequence=sequence,
            title=title,
            status=TaskStatus.DRAFT,
            description=description,
            agent_responses=[],
            response=None,
        )
