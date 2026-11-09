from agent.application.agent.query_agent import QueryAgent
from agent.application.service.tool_executor import ToolExecutor
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.tool.tool_registry import ToolRegistry
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger


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

    def run(self, conversation_id: ConversationId) -> str:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        tools = self._tool_registry.definitions()

        with self._logger.status(message="Analyzing user request"):
            result = self._agent.run(conversation, tools)
        self._logger.debug(result)

        self._logger.info("User request analysis completed")
