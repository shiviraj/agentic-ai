from dataclasses import dataclass

from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.final_response import FinalResponse
from agent.domain.vo.interaction_id import InteractionId
from agent.domain.vo.user_request import UserRequest
from agent.shared.domain.entity import Entity


@dataclass(eq=False)
class Interaction(Entity[InteractionId]):
    request: UserRequest
    response: FinalResponse | None
    agent_responses: list[AgentResponse]

    @classmethod
    def create(cls, request: UserRequest) -> "Interaction":
        return cls(id=InteractionId.generate(), request=request, agent_responses=[], response=None)
