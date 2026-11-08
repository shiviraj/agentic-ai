from agent.domain.aggregate.conversation import Conversation
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.task.task import Task
from agent.domain.vo.conversation_id import ConversationId


class ConversationRepositoryImpl(ConversationRepository):
    def __init__(self) -> None:
        self._conversations: dict[str, Task] = {}

    def save(self, conversation: Conversation) -> Conversation:
        self._conversations[conversation.id.value] = conversation
        return conversation

    def find_by_conversation_id(self, conversation_id: ConversationId) -> Conversation | None:
        return self._conversations[conversation_id.value]
