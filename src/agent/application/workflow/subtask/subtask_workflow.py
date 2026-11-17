from agent.application.service.execution.execution_registry import ExecutionRegistry
from agent.application.service.subtask_planning_service import SubtaskPlanningService
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.entity.subtask import Subtask


class SubtaskWorkflow:
    def __init__(
        self,
        subtask_planning_service: SubtaskPlanningService,
        execution_registry: ExecutionRegistry,
    ):
        self._subtask_planning_service = subtask_planning_service
        self._execution_registry = execution_registry

    async def execute(self, data: WorkflowInput, subtask: Subtask) -> WorkflowResult:
        execution_plan = self._subtask_planning_service.plan(data, subtask)
        for step in execution_plan.steps:
            await self._execution_registry.execute(data, step)

        # verification subtask

        return WorkflowResult(content=str(execution_plan))
