from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.agent.agent import Agent
from agent.domain.aggregate.task import Task
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class DecompositionService:
    def __init__(
        self,
        agent: Agent[Task],
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
    ) -> None:
        self._agent = agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._logger = Logger("DecompositionService")

    def decompose(self, data: WorkflowInput) -> Task:
        self._conversation_service.add_user_message(data.conversation_id, self._build_prompt(data.user_request))
        with self._logger.status(message="Decomposition task..."):
            context = self._conversation_context_service.get_context(data.conversation_id)
            result = self._agent.execute(context)
        self._logger.debug(result)
        self._conversation_service.add_assistant_message(data.conversation_id, str(result))
        self._conversation_service.add_agent_response(data.conversation_id, "DecompositionAgent", result)
        self._logger.info("Successfully decomposed task")
        return result

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are a Senior Backend Engineering Task Decomposition Agent specializing in
        TypeScript backend development.

        Your responsibility is to break an analyzed and understood task into small,
        logical, actionable implementation subtasks.

        User request:
        {user_request.value}
        """
