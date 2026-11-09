from agent.application.agent.engineer_agent import EngineerAgent
from agent.application.service.dto.analyze_user_request_result import RequestCategory
from agent.application.service.query_agent_service import QueryAgentService
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class EngineerAgentService:
    def __init__(
        self,
        agent: EngineerAgent,
        query_agent_service: QueryAgentService,
        conversation_repository: ConversationRepository,
    ):
        self._agent = agent
        self._query_agent_service = query_agent_service
        self._conversation_repository = conversation_repository
        self._logger = Logger("EngineerAgentService")

    async def run(self, request: UserRequest, conversation_id: ConversationId) -> str:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        conversation.add(Message(Role.USER, request.value))

        with self._logger.status(message="Analyzing user request"):
            analyze_result = self._agent.analyze(conversation)
        self._logger.debug(analyze_result)
        self._logger.info("User request analysis completed")

        if analyze_result.category == RequestCategory.CONVERSATION:
            conversation.add(Message(Role.ASSISTANT, analyze_result.response))
            self._conversation_repository.save(conversation)
            return analyze_result.response

        if analyze_result.category == RequestCategory.QUERY:
            return await self._query_agent_service.run(conversation.id)
        if analyze_result.category == RequestCategory.TASK:
            return analyze_result.response
        return analyze_result.response
