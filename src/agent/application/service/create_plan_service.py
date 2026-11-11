from agent.application.agent.plan_agent import PlanAgent
from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class CreatePlanService:
    def __init__(
        self,
        agent: PlanAgent,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._logger = Logger("CreatePlanService")

    def run(self, conversation_id: ConversationId) -> ImplementationPlan:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        plan = self._create_implementation_plan(conversation)
        self._conversation_repository.save(conversation)
        return plan

    def _create_implementation_plan(self, conversation: Conversation) -> ImplementationPlan:
        conversation.add(Message(role=Role.USER, content=self._build_content(conversation)))
        with self._logger.status(message="Creating implementation plan"):
            result = self._agent.run(conversation)
        self._logger.debug(result)
        conversation.add(Message(role=Role.ASSISTANT, content=str(result)))
        conversation.add_response(AgentResponse(str(result)))
        self._conversation_repository.save(conversation)
        self._logger.info("Creating implementation plan completed")
        return result

    def _build_content(self, conversation: Conversation) -> str:
        return f"""
            You are an intelligent Plan Agent for a TypeScript backend engineering team.
            Your responsibility is to create an implementation plan.

            User request:
            {conversation.get_request().value}

            Agent responses:
            {conversation.build_agent_response()}

            Agent History:
            {conversation.build_agent_history()}
            """
