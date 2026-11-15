from agent.application.service.analysis_service import AnalysisService
from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.vo.task_analysis import AnalysisStatus


class TaskWorkflow(Workflow):
    def __init__(self, analysis_service: AnalysisService):
        self._analysis_service = analysis_service

    async def execute(self, data: WorkflowInput) -> WorkflowResult:
        analysis_result = await self._analysis_service.analyze(data.conversation_id, data.user_request)
        if analysis_result.status == AnalysisStatus.NEEDS_CLARIFICATION:
            return WorkflowResult(str(analysis_result))

        return WorkflowResult(content=analysis_result.summary)
