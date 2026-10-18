from typing import Callable

from agent.application.port.step_executor import StepExecutor
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.entity.plan_step import PlanStep


class ExecutePlan:

    def __init__(
            self,
            step_executor: StepExecutor,
            tool_executor: ToolExecutor,
            display_step_executing: Callable[[PlanStep], None]
    ) -> None:
        self._step_executor = step_executor
        self._tool_executor = tool_executor
        self._display_step_executing = display_step_executing

    def execute(self, plan: ImplementationPlan) -> None:
        for step in plan.steps:
            self._display_step_executing(step)
            self._step_executor.execute(step, self._tool_executor)
