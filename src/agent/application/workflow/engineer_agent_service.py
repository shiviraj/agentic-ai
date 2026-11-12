from agent.application.agent.engineer_agent import EngineerAgent
from agent.application.port.dto.llm_response import ChatResponse
from agent.application.service.dto.analyze_user_request_result import RequestCategory
from agent.application.workflow.query_agent_service import QueryAgentService
from agent.application.workflow.task_agent_service import TaskAgentService
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger


class EngineerAgentService:
    def __init__(
        self,
        agent: EngineerAgent,
        query_agent_service: QueryAgentService,
        task_agent_service: TaskAgentService,
        conversation_repository: ConversationRepository,
    ):
        self._agent = agent
        self._query_agent_service = query_agent_service
        self._task_agent_service = task_agent_service
        self._conversation_repository = conversation_repository
        self._logger = Logger("EngineerAgentService")

    async def run(self, conversation_id: ConversationId) -> ChatResponse:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        conversation.add(Message(role=Role.USER, content=self._build_content(conversation)))
        self._conversation_repository.save(conversation)

        with self._logger.status(message="Analyzing user request"):
            analyze_result = self._agent.analyze(conversation)
        self._logger.debug(analyze_result)
        self._logger.info("User request analysis completed")

        if analyze_result.category == RequestCategory.CONVERSATION:
            conversation.add(Message(Role.ASSISTANT, analyze_result.response))
            conversation.add_response(AgentResponse(response=analyze_result.response))
            self._conversation_repository.save(conversation)
            return ChatResponse(analyze_result)

        if analyze_result.category == RequestCategory.QUERY:
            return await self._query_agent_service.run(conversation.id)
        if analyze_result.category == RequestCategory.TASK:
            return await self._task_agent_service.run(conversation.id)
        return analyze_result.response

    def _build_content(self, conversation: Conversation) -> str:
        return f"""
            You are the first step of an assistant for a TypeScript backend team.
            Read the user's message and choose one category. Do not solve the request.

            User request:
            {conversation.get_request().value}

            Agent responses:
            {conversation.build_agent_response()}

            Agent History:
            {conversation.build_agent_history()}
            """
