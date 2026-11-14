from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.service.tool_executor import ToolExecutor
from agent.domain.agent.investigation_agent import InvestigationAgent
from agent.domain.tool.finish_tool_definition import FINISH_TOOL_DEFINITION
from agent.domain.tool.tool_registry import ToolRegistry
from agent.domain.vo.chat_response import ChatResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class InvestigationService:
    def __init__(
        self,
        agent: InvestigationAgent,
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
        tools = [*self._tool_registry.definitions(), FINISH_TOOL_DEFINITION]

        for _ in range(0, MAX_ITERATIONS):
            with self._logger.status(message="Investigating project..."):
                context = self._conversation_context_service.get_context(conversation_id)
                result = self._agent.execute(context, tools)
            self._logger.debug(result)

            if result.finished:
                summary = result.content
                break

            if result.tools:
                self._conversation_service.add_tool_calls(conversation_id, result.tools)
                for tool_call in result.tools:
                    tool_result = await self._tool_executor.execute(tool_call)
                    self._conversation_service.add_tool_result(conversation_id, tool_call, tool_result)
                    self._logger.debug(tool_result)

            if result.content:
                self._conversation_service.add_assistant_message(conversation_id, result.content)

            if not result.tools and not result.content:
                self._conversation_service.add_user_message(
                    conversation_id,
                    "Your previous response was empty. "
                    "You must continue the investigation by calling at least"
                    "one available tool. If the investigation is complete "
                    "or cannot continue, call the finish tool. "
                    "Do not return an empty response or plain text.",
                )

        self._conversation_service.add_assistant_message(conversation_id, summary)
        self._logger.debug(summary)
        self._logger.info("Successfully completed investigation")
        return ChatResponse(summary)

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are an intelligent Investigation Agent for a TypeScript backend engineering team.

        Your responsibility is to investigate user requests, gather the required information
        using available tools, and return structured findings through the `__agent__::finish` tool.

        You are NOT responsible for generating the final conversational response.

        User request:
        {user_request.value}
        """
