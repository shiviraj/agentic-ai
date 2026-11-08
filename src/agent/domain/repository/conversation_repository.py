from abc import abstractmethod

from agent.domain.aggregate.conversation import Conversation
from agent.domain.vo.conversation_id import ConversationId


class ConversationRepository:
    @abstractmethod
    def save(self, conversation: Conversation) -> Conversation: ...

    @abstractmethod
    def find_by_conversation_id(self, conversation_id: ConversationId) -> Conversation | None: ...
