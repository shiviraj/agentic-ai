from agent.application.agent.query_agent import QueryAgent
from agent.application.service.tool_executor import ToolExecutor
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.tool.tool_registry import ToolRegistry
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class QueryAgentService:
    def __init__(
        self,
        agent: QueryAgent,
        conversation_repository: ConversationRepository,
        tool_executor: ToolExecutor,
        tool_registry: ToolRegistry,
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._logger = Logger("QueryAgentService")
        self._tool_executor = tool_executor
        self._tool_registry = tool_registry

    async def run(self, conversation_id: ConversationId) -> str:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        query_response = await self._analyze_query(conversation)
        return query_response
        # return self._summarize_.run(conversation_id, query_response)

    async def _analyze_query(self, conversation: Conversation) -> str:
        summary = "Unable to find user query response"
        tools = self._tool_registry.definitions()
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
        self._logger.info("User request analysis completed")
        return summary
