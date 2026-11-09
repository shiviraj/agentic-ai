from agent.application.agent.query_agent import QueryAgent
from agent.application.port.dto.llm_response import ChatResponse
from agent.application.service.summarize_agent_service import SummarizeAgentService
from agent.application.service.tool_executor import ToolExecutor
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.tool.tool_registry import ToolRegistry
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class QueryAgentService:
    def __init__(
        self,
        agent: QueryAgent,
        summarize_agent_service: SummarizeAgentService,
        conversation_repository: ConversationRepository,
        tool_executor: ToolExecutor,
        tool_registry: ToolRegistry,
    ) -> None:
        self._agent = agent
        self._summarize_agent_service = summarize_agent_service
        self._conversation_repository = conversation_repository
        self._logger = Logger("QueryAgentService")
        self._tool_executor = tool_executor
        self._tool_registry = tool_registry

    async def run(self, conversation_id: ConversationId) -> ChatResponse:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        query_response = await self._analyze_query(conversation)
        conversation.add_response(AgentResponse(query_response.content))
        return self._summarize_agent_service.run(conversation_id)

    async def _analyze_query(self, conversation: Conversation) -> ChatResponse:
        summary = "Unable to find user query response"
        tools = self._tool_registry.definitions()
        conversation.add(Message(role=Role.USER, content=self._build_content(conversation)))
        for _ in range(0, MAX_ITERATIONS):
            with self._logger.status(message="Analyzing user request"):
                result = self._agent.run(conversation, tools)
            self._logger.debug(result)
            if result.finished:
                summary = result.content
                break
            for tool_call in result.tools:
                tool_result = await self._tool_executor.execute(tool_call)
                self._logger.debug(tool_result)
                conversation.add(Message(role=Role.ASSISTANT, content="", tool_calls=[tool_call]))
                conversation.add(Message(role=Role.TOOL, tool_name=tool_call.name, content=str(tool_result)))
            if result.content:
                conversation.add(Message(role=Role.ASSISTANT, content=result.content))
            if not result.tools and not result.content:
                conversation.add(
                    Message(
                        role=Role.USER,
                        content=(
                            "Your previous response was empty. "
                            "You must continue the investigation by calling exactly "
                            "one available tool. If the investigation is complete "
                            "or cannot continue, call the finish tool. "
                            "Do not return an empty response or plain text."
                        ),
                    )
                )
        self._conversation_repository.save(conversation)
        self._logger.info("Query analysis completed")
        return ChatResponse(summary)

    def _build_content(self, conversation: Conversation) -> str:
        return f"""
            You are an intelligent Query Agent for a TypeScript backend engineering team.
            Your responsibility is to investigate user requests, gather the required information
            using available tools, and return structured findings through the `finish` tool.

            User request:
            {conversation.get_request().value}

            Agent responses:
            {conversation.build_agent_response()}
            """
