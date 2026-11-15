from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.agent.conversation_agent import ConversationAgent
from agent.domain.vo.chat_response import ChatResponse
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class ResponseService:
    def __init__(
        self,
        agent: ConversationAgent,
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
    ):
        self._agent = agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._logger = Logger("ConversationWorkflow")

    def execute(self, data: WorkflowInput) -> ChatResponse:
        self._conversation_service.add_user_message(data.conversation_id, self._build_prompt(data.user_request))
        with self._logger.status("Generating response for user request..."):
            context = self._conversation_context_service.get_context(data.conversation_id)
            response = self._agent.execute(context)

        self._logger.debug(response)
        self._conversation_service.add_agent_response(
            data.conversation_id, agent_name="ConversationAgent", response=response
        )
        self._logger.info("Successfully responded to user request")
        self._conversation_service.add_assistant_message(data.conversation_id, response.content)
        return ChatResponse(content=response.content)

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are the Conversation Agent for an AI-powered Senior Backend Engineer system.

        Your responsibility is to generate clear, natural, and helpful responses to the user
        based on their latest request, relevant conversation history, and the result provided
        by the calling workflow.

        You are the final communication layer between the system and the user.


        User request:
        {user_request.value}
        """
