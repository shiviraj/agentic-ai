from agent.application.agent.summary_agent import SummaryAgent
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger


class SummarizeAgentService:
    def __init__(
        self,
        agent: SummaryAgent,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._logger = Logger("SummarizeAgentService")

    async def run(self, conversation_id: ConversationId) -> str:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        with self._logger.status(message="Summarizing response..."):
            result = self._agent.run(conversation)

