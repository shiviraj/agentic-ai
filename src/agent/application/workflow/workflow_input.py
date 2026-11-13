from dataclasses import dataclass

from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.user_request import UserRequest


@dataclass(frozen=True)
class WorkflowInput:
    conversation_id: ConversationId
    user_request: UserRequest
