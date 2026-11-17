from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.service.execution.execution import Execution
from agent.application.service.execution.execution_result import ExecutionResult
from agent.application.service.tool_executor import ToolExecutor
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.agent.agent import Agent
from agent.domain.aggregate.execution_plan import ExecutionStep
from agent.domain.tool.tool_registry import ToolRegistry
from agent.domain.vo.chat_response import ChatResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.tool_response import ToolResponse
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class CodeReviewExecution(Execution):
    def __init__(
        self,
        agent: Agent[ChatResponse],
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
        tool_executor: ToolExecutor,
        tool_registry: ToolRegistry,
    ) -> None:
        self._agent = agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._tool_registry = tool_registry
        self._tool_executor = tool_executor
        self._logger = Logger("CodeReviewExecution")

    async def execute(self, data: WorkflowInput, step: ExecutionStep) -> ExecutionResult:
        self._conversation_service.add_user_message(data.conversation_id, self._build_prompt(data.user_request, step))
        summary = "Error: Unable to investigate project"

        for _ in range(0, MAX_ITERATIONS):
            with self._logger.status(message="Reviewing code..."):
                context = self._conversation_context_service.get_context(data.conversation_id)
                result = self._agent.execute_tools(context, self._tool_registry.definitions())
            self._logger.debug(result)
            await self._handle_response(result, data.conversation_id)
            if result.finished:
                summary = result.content
                break

        self._conversation_service.add_assistant_message(data.conversation_id, summary)
        self._logger.debug(summary)
        self._logger.info("Successfully reviewed code")
        return ExecutionResult(summary)

    async def _handle_response(self, result: ToolResponse, conversation_id: ConversationId) -> None:
        if result.tools:
            self._conversation_service.add_tool_calls(conversation_id, tuple(result.tools))
            for tool_call in result.tools:
                tool_result = await self._tool_executor.execute(tool_call)
                self._conversation_service.add_tool_result(conversation_id, tool_call, tool_result)
                self._logger.debug(tool_result)

        if result.content:
            self._conversation_service.add_assistant_message(conversation_id, result.content)

    def _build_prompt(self, user_request: UserRequest, step: ExecutionStep) -> str:
        return f"""
        You are a Code Review Agent working as a Senior Software Architect
        and experienced Backend Code Reviewer.

        You are reviewing changes in an existing software project.

        User request:
        {user_request.value}

        Execution step:
        {step}
        """
