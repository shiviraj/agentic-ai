from agent.application.agent.task_agent import TaskAgent
from agent.application.workflow.query_agent_service import QueryAgentService
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.policy.task_analysis_policy import TaskAnalysisPolicy
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.task_analysis import TaskAnalysis, TaskAnalysisStatus
from agent.shared.domain.exception.policy_violation_exception import PolicyViolationError
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class AnalyzeTaskService:
    def __init__(
        self,
        agent: TaskAgent,
        policy: TaskAnalysisPolicy,
        query_agent_service: QueryAgentService,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._agent = agent
        self._policy = policy
        self._query_agent_service = query_agent_service
        self._conversation_repository = conversation_repository
        self._logger = Logger("TaskAgentService")

    async def run(self, conversation_id: ConversationId) -> TaskAnalysis:
        conversation = self._conversation_repository.find_by_conversation_id(conversation_id)
        analysis_result = None
        for _ in range(MAX_ITERATIONS):
            analysis_result = await self._analyze_task(conversation)
            try:
                self._policy.evaluate(analysis_result).enforce("Invalid task analysis result")
            except PolicyViolationError as e:
                conversation.add(
                    Message(
                        role=Role.USER,
                        content=f"Your previous response is invalid: {e}",
                    )
                )
                continue
            if (
                analysis_result.status == TaskAnalysisStatus.NEEDS_CLARIFICATION
                or analysis_result.status == TaskAnalysisStatus.READY
            ):
                break

            if analysis_result.status == TaskAnalysisStatus.NEEDS_INVESTIGATION:
                conversation.add(Message(role=Role.USER, content=str(analysis_result.open_questions)))
                answer = await self._query_agent_service.analyze_query(conversation)
                conversation.add(
                    Message(
                        role=Role.ASSISTANT,
                        content=str({"questions": analysis_result.open_questions, "answer": answer.content}),
                    )
                )

        self._conversation_repository.save(conversation)
        self._logger.info("Task analysis completed")
        return analysis_result

    async def _analyze_task(self, conversation: Conversation) -> TaskAnalysis:
        conversation.add(Message(role=Role.USER, content=self._build_content(conversation)))
        with self._logger.status(message="Analyzing task"):
            result = self._agent.run(conversation)
        self._logger.debug(result)
        conversation.add(Message(role=Role.ASSISTANT, content=str(result)))
        conversation.add_response(AgentResponse(str(result)))
        self._conversation_repository.save(conversation)
        return result

    def _build_content(self, conversation: Conversation) -> str:
        return f"""
            You are an intelligent Task Agent for a TypeScript backend engineering team.
            Your responsibility is to investigate user task request, create a summary and requirements.

            list down all open questions in requirements if you are not sure and which is really
            needed for task implementations

            User request:
            {conversation.get_request().value}

            Agent responses:
            {conversation.build_agent_response()}

            Agent History:
            {conversation.build_agent_history()}
            """
