from agent.application.agent.subtask_planning_agent import SubtaskPlanningAgent
from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.task import Task
from agent.domain.entity.subtask import Subtask
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger


class PlanSubtaskService:
    def __init__(
        self,
        agent: SubtaskPlanningAgent,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._logger = Logger("PlanSubtaskService")

    def run(self, conversation_id: ConversationId, subtask: Subtask) -> Task:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        conversation.add(Message(role=Role.USER, content=self._build_content(conversation, subtask)))
        with self._logger.status(message="Planning subtask"):
            result = self._agent.run(conversation)
        self._logger.debug(result)
        conversation.add(Message(role=Role.ASSISTANT, content=str(result)))
        conversation.add_response(AgentResponse(str(result)))
        self._conversation_repository.save(conversation)
        self._logger.info("Subtask planning completed")
        return result

    def _build_content(self, conversation: Conversation, subtask: Subtask) -> str:
        return f"""
            You are a Senior Software Engineer responsible for planning the execution
            of a single software development subtask.

            Your responsibility is to create an ordered execution plan that can be
            executed by specialized engineering agents.

            Actual subtask:
            {subtask}

            User request:
            {conversation.get_request().value}

            Agent responses:
            {conversation.build_agent_response()}

            Agent History:
            {conversation.build_agent_history()}
            """
