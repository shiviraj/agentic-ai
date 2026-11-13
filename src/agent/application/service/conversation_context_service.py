from agent.domain.entity.message import Message
from agent.domain.errors import DataNotFoundError
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.conversation_id import ConversationId


class ConversationContextService:
    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repository = conversation_repository

    def get_context(self, conversation_id: ConversationId) -> tuple[Message, ...]:
        conversation = self._conversation_repository.find_by_id(conversation_id)
        if conversation is None:
            raise DataNotFoundError(f"Conversation not found for: {conversation_id}")
        return tuple(conversation.messages)
