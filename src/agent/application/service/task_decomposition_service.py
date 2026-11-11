from agent.application.agent.task_decomposition_agent import TaskDecompositionAgent
from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.task import Task
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger


class TaskDecompositionService:
    def __init__(
        self,
        agent: TaskDecompositionAgent,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._logger = Logger("TaskDecompositionService")

    def run(self, conversation_id: ConversationId) -> Task:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        conversation.add(Message(role=Role.USER, content=self._build_content(conversation)))
        with self._logger.status(message="Decomposition task"):
            result = self._agent.run(conversation)
        self._logger.debug(result)
        conversation.add(Message(role=Role.ASSISTANT, content=str(result)))
        conversation.add_response(AgentResponse(str(result)))
        self._conversation_repository.save(conversation)
        self._logger.info("Task decomposition completed")
        return result

    def _build_content(self, conversation: Conversation) -> str:
        return f"""
            You are an intelligent decomposition Agent for a TypeScript backend engineering team.
            Your responsibility is to task decomposition in multiple subtasks.

            User request:
            {conversation.get_request().value}

            Agent responses:
            {conversation.build_agent_response()}

            Agent History:
            {conversation.build_agent_history()}
            """
