from agent.application.port.step_executor import StepExecutor
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.vo.step_result import StepResult
from agent.shared.logger.logger import Logger


class ExecutePlan:
    def __init__(self, step_executor: StepExecutor, tool_executor: ToolExecutor) -> None:
        self._step_executor = step_executor
        self._tool_executor = tool_executor
        self._logger = Logger("ExecutePlan")

    def execute(self, plan: ImplementationPlan) -> None:
        previous_results: list[StepResult] = []
        for step in plan.steps:
            self._logger.info(f"{step.sequence}. {step.title}\n{step.description}", "cyan")
            result = self._step_executor.execute(step, self._tool_executor, previous_results)
            previous_results.append(result)
            if not result.success:
                # Do not execute dependent steps after a failure or blocker.
                self._logger.info(f"Step execution failed {result}", "red bold")
                break
