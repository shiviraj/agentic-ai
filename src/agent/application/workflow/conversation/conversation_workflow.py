from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.conversation.conversation_result import ConversationResult
from agent.application.workflow.workflow import Workflow
from agent.domain.agent.conversation_agent import ConversationAgent
from agent.domain.vo.conversation_id import ConversationId


class ConversationWorkflow(Workflow):
    def __init__(self, agent: ConversationAgent, conversation_service: ConversationService):
        self._agent = agent
        self._conversation_service = conversation_service

    def execute(self, data: ConversationId) -> ConversationResult:
        conversation = self._conversation_service.get_conversation(input.conversation_id)
        response = self._agent.execute(conversation.messages)
        return response
