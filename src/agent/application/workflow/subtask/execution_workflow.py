from agent.application.service.subtask_planning_service import SubtaskPlanningService
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.entity.subtask import Subtask


class ExecutionWorkflow:
    def __init__(self, subtask_planning_service: SubtaskPlanningService):
        self._subtask_planning_service = subtask_planning_service

    async def execute(self, data: WorkflowInput, subtask: Subtask) -> WorkflowResult:
        execution_plan = self._subtask_planning_service.plan(data, subtask)
        return WorkflowResult(content=str(execution_plan))
