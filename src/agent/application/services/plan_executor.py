from agent.application.port.step_approval import StepApproval
from agent.application.port.step_executor import StepExecutor
from agent.domain.aggregate.implementation_plan import ImplementationPlan


class PlanExecutor:

    def __init__(self, step_executor: StepExecutor, step_approval: StepApproval):
        self._step_executor = step_executor
        self._step_approval = step_approval

    def execute(self, plan: ImplementationPlan) -> None:
        for step in plan.steps:
            if not self._step_approval.approve(step):
                return
            self._step_executor.execute(step)
