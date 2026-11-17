from agent.application.service.execution.code_review_execution import CodeReviewExecution
from agent.application.service.execution.execution import Execution
from agent.application.service.execution.execution_result import ExecutionResult
from agent.application.service.execution.implementation_execution import ImplementationExecution
from agent.application.service.execution.test_design_execution import TestDesignExecution
from agent.application.service.execution.test_verification_execution import TestVerificationExecution
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.aggregate.execution_plan import ExecutionAgent, ExecutionStep
from agent.domain.errors import DataNotFoundError


class ExecutionRegistry:
    def __init__(
        self,
        implementation_execution: ImplementationExecution,
        code_review_execution: CodeReviewExecution,
        test_design_execution: TestDesignExecution,
        test_verification_execution: TestVerificationExecution,
    ):
        self._execution_maps: dict[ExecutionAgent, Execution] = {
            ExecutionAgent.IMPLEMENTATION: implementation_execution,
            ExecutionAgent.CODE_REVIEW: code_review_execution,
            ExecutionAgent.TEST_DESIGN: test_design_execution,
            ExecutionAgent.TEST_VERIFICATION: test_verification_execution,
        }

    async def execute(self, data: WorkflowInput, step: ExecutionStep) -> ExecutionResult:
        execution = self._get_execution(step.agent)
        return await execution.execute(data, step)

    def _get_execution(self, agent: ExecutionAgent) -> Execution:
        execution = self._execution_maps.get(agent)
        if execution is None:
            raise DataNotFoundError(f"Execution not found for {agent.value}")
        return execution
