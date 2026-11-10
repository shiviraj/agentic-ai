from ollama import ChatResponse

from agent.application.agent.summary_agent import SummaryAgent
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.logger.logger import Logger


class SummarizeAgentService:
    def __init__(
        self,
        agent: SummaryAgent,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._agent = agent
        self._conversation_repository = conversation_repository
        self._logger = Logger("SummarizeAgentService")

    def run(self, conversation_id: ConversationId) -> ChatResponse:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        conversation.add(Message(role=Role.USER, content=self._build_content(conversation)))
        with self._logger.status(message="Summarizing response..."):
            result = self._agent.run(conversation=conversation)
        conversation.add(Message(role=Role.ASSISTANT, content=result.content))
        conversation.add_response(AgentResponse(result.content))
        self._conversation_repository.save(conversation)
        self._logger.info("Response summarization completed")
        return result

    def _build_content(self, conversation: Conversation) -> str:
        return f"""
        You are an AI Response Agent for a TypeScript backend engineering team.
        Your responsibility is to convert investigation findings into clear,
        accurate, and natural-language responses for the user.

        User request:
        {conversation.get_request().value}

        Agent responses:
        {conversation.build_agent_response()}

        Agent History:
        {conversation.build_agent_history()}
        """
