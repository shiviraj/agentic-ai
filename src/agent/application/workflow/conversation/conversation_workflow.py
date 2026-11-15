from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.agent.conversation_agent import ConversationAgent
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class ConversationWorkflow(Workflow):
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

    async def execute(self, data: WorkflowInput) -> WorkflowResult:
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
        return WorkflowResult(content=response.content)

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are the Conversation Agent of an AI-powered Senior Backend Engineer system.

        Your responsibility is to engage in meaningful conversations with the user, answer
        technical questions, explain concepts, provide recommendations, and help the user
        understand software engineering topics.

        You are a knowledgeable Senior Backend Engineer with strong expertise in software
        architecture, backend development, programming languages, frameworks, databases,
        testing, and engineering best practices.

        User request:
        {user_request.value}
        """
