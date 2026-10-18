from agent.application.services.tool_executor import ToolExecutor
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.step_result import StepResult


class StepExecutor:
    def execute(self, step: PlanStep, tool_executor: ToolExecutor) -> StepResult:
        ...
