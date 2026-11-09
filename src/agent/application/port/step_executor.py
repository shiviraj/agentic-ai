from agent.application.service.tool_executor import ToolExecutor
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.step_result import StepResult


class StepExecutor:
    def execute(
        self, step: PlanStep, tool_executor: ToolExecutor, previous_results: list[StepResult]
    ) -> StepResult: ...
