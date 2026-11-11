from agent.application.port.dto.llm_response import ChatResponse
from agent.application.service.analyze_task_service import AnalyzeTaskService
from agent.application.service.create_plan_service import CreatePlanService
from agent.application.service.summarize_agent_service import SummarizeAgentService
from agent.application.workflow.query_agent_service import QueryAgentService
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.task_analysis import TaskAnalysisStatus
from agent.shared.logger.logger import Logger


class TaskAgentService:
    def __init__(
        self,
        analyze_task_service: AnalyzeTaskService,
        create_plan_service: CreatePlanService,
        summarize_agent_service: SummarizeAgentService,
        query_agent_service: QueryAgentService,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._analyze_task_service = analyze_task_service
        self._summarize_agent_service = summarize_agent_service
        self._create_plan_service = create_plan_service
        self._query_agent_service = query_agent_service
        self._conversation_repository = conversation_repository
        self._logger = Logger("TaskAgentService")

    async def run(self, conversation_id: ConversationId) -> ChatResponse:
        analysis_result = await self._analyze_task_service.run(conversation_id=conversation_id)
        if analysis_result.status == TaskAnalysisStatus.NEEDS_CLARIFICATION:
            return self._summarize_agent_service.run(conversation_id)

        plan = self._create_plan_service.run(conversation_id)
        print(plan)
        return self._summarize_agent_service.run(conversation_id)
