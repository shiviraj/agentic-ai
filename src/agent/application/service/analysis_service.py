from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.service.investigation_service import InvestigationService
from agent.domain.agent.agent import Agent
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.task_analysis import AnalysisResult, AnalysisStatus
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 10


class AnalysisService:
    def __init__(
        self,
        agent: Agent[AnalysisResult],
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
        investigation_service: InvestigationService,
    ) -> None:
        self._agent = agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._investigation_service = investigation_service
        self._logger = Logger("AnalysisService")

    async def analyze(self, conversation_id: ConversationId, user_request: UserRequest) -> AnalysisResult:
        for _ in range(MAX_ITERATIONS):
            self._conversation_service.add_user_message(conversation_id, self._build_prompt(user_request))
            with self._logger.status(message="Analyzing task..."):
                context = self._conversation_context_service.get_context(conversation_id)
                result = self._agent.execute(context)
            self._logger.debug(result)
            self._conversation_service.add_assistant_message(conversation_id, result.summary)
            self._conversation_service.add_agent_response(conversation_id, "AnalysisAgent", result)

            if result.status == AnalysisStatus.NEEDS_CLARIFICATION or result.status == AnalysisStatus.READY:
                self._logger.info("Successfully analyzed task")
                return result

            if result.status == AnalysisStatus.NEEDS_INVESTIGATION:
                questions = [question.question for question in result.open_questions]
                await self._investigation_service.investigate(conversation_id, UserRequest("\n\n".join(questions)))

        self._logger.error("Failed to analyze task")
        return AnalysisResult(AnalysisStatus.FAILED, "", "", [])

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are an intelligent Task Agent for a TypeScript backend engineering team.
        Your responsibility is to investigate user task request, create a summary and requirements.

        list down all open questions in requirements if you are not sure and which is really
        needed for task implementations

        User request:
        {user_request.value}
        """
