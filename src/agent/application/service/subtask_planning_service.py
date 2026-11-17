from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.agent.agent import Agent
from agent.domain.aggregate.execution_plan import ExecutionPlan
from agent.domain.entity.subtask import Subtask
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class SubtaskPlanningService:
    def __init__(
        self,
        agent: Agent[ExecutionPlan],
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
    ) -> None:
        self._agent = agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._logger = Logger("SubtaskPlanningService")

    def plan(self, data: WorkflowInput, subtask: Subtask) -> ExecutionPlan:
        self._conversation_service.add_user_message(
            data.conversation_id, self._build_prompt(subtask, data.user_request)
        )
        with self._logger.status(message="Subtask planning..."):
            context = self._conversation_context_service.get_context(data.conversation_id)
            result = self._agent.execute(context)
        self._logger.debug(result)

        self._conversation_service.add_assistant_message(data.conversation_id, str(result))
        self._conversation_service.add_agent_response(data.conversation_id, "SubtaskPlanningAgent", result)
        self._logger.info("Successfully planned subtask")
        return result

    def _build_prompt(self, subtask: Subtask, user_request: UserRequest) -> str:
        return f"""
        You are a Senior Software Engineer responsible for planning the execution
        of a single software development subtask.

        Your responsibility is to create an ordered execution plan that can be
        executed by specialized engineering agents.

        User request:
        {user_request.value}

        Actual subtask:
        {subtask}
        """
