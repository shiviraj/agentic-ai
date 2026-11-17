from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.service.tool_executor import ToolExecutor
from agent.domain.agent.agent import Agent
from agent.domain.tool.tool_registry import ToolRegistry
from agent.domain.vo.chat_response import ChatResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.tool_response import ToolResponse
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class InvestigationService:
    def __init__(
        self,
        agent: Agent[ChatResponse],
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
    ) -> None:
        self._agent = agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._tool_registry = tool_registry
        self._tool_executor = tool_executor
        self._logger = Logger("InvestigationService")

    async def investigate(self, conversation_id: ConversationId, user_request: UserRequest) -> ChatResponse:
        self._conversation_service.add_user_message(conversation_id, self._build_prompt(user_request))
        summary = "Error: Unable to investigate project"

        for _ in range(0, MAX_ITERATIONS):
            with self._logger.status(message="Investigating project..."):
                context = self._conversation_context_service.get_context(conversation_id)
                result = self._agent.execute_tools(context, self._tool_registry.definitions())
            self._logger.debug(result)
            await self._handle_response(result, conversation_id)
            if result.finished:
                summary = result.content
                break

        self._conversation_service.add_assistant_message(conversation_id, summary)
        self._logger.debug(summary)
        self._logger.info("Successfully completed investigation")
        return ChatResponse(summary)

    async def _handle_response(self, result: ToolResponse, conversation_id: ConversationId) -> None:
        if result.tools:
            self._conversation_service.add_tool_calls(conversation_id, tuple(result.tools))
            for tool_call in result.tools:
                tool_result = await self._tool_executor.execute(tool_call)
                self._conversation_service.add_tool_result(conversation_id, tool_call, tool_result)
                self._logger.debug(tool_result)

        if result.content:
            self._conversation_service.add_assistant_message(conversation_id, result.content)

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are an intelligent Investigation Agent for a TypeScript backend engineering team.

        Your responsibility is to investigate user requests, gather the required information
        using available tools, and return structured findings through the `__agent__::finish` tool.

        You are NOT responsible for generating the final conversational response.

        User request:
        {user_request.value}
        """
