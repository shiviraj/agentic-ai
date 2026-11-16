from agent.application.service.analysis_service import AnalysisService
from agent.application.service.decomposition_service import DecompositionService
from agent.application.workflow.subtask.execution_workflow import ExecutionWorkflow
from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.vo.task_analysis import AnalysisStatus


class TaskWorkflow(Workflow):
    def __init__(
        self,
        analysis_service: AnalysisService,
        decomposition_service: DecompositionService,
        execution_workflow: ExecutionWorkflow,
    ):
        self._analysis_service = analysis_service
        self._decomposition_service = decomposition_service
        self._execution_workflow = execution_workflow

    async def execute(self, data: WorkflowInput) -> WorkflowResult:
        analysis_result = await self._analysis_service.analyze(data.conversation_id, data.user_request)
        if analysis_result.status == AnalysisStatus.NEEDS_CLARIFICATION:
            return WorkflowResult(str(analysis_result))
        task = self._decomposition_service.decompose(data)
        for subtask in task.sub_tasks:
            await self._execution_workflow.execute(data, subtask)
        return WorkflowResult(content=analysis_result.summary)
