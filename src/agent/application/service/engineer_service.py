from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.agent.dto.engineer_agent_result import EngineerAgentResult
from agent.domain.agent.engineer_agent import EngineerAgent
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class EngineerService:
    def __init__(
        self,
        agent: EngineerAgent,
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
    ):
        self._agent = agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._logger = Logger("EngineerService")

    def execute(self, data: WorkflowInput) -> EngineerAgentResult:
        self._conversation_service.add_user_message(data.conversation_id, self._build_prompt(data.user_request))
        with self._logger.status("Classifying user request..."):
            context = self._conversation_context_service.get_context(data.conversation_id)
            classification = self._agent.execute(context)

        self._logger.debug(classification)
        self._conversation_service.add_agent_response(
            data.conversation_id, agent_name="EngineerAgent", response=classification
        )
        self._logger.info("Successfully classified user request")
        return classification

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are the Engineer Agent, the primary request classification agent
        for an AI-powered Senior Backend Engineer system.

        Your responsibility is to understand the user's latest request,
        consider the relevant conversation history, and classify the request

        User request:
        {user_request.value}
        """
