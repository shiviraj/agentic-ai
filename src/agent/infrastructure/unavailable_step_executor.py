from agent.application.port.step_executor import StepExecutor
from agent.domain.entity.plan_step import PlanStep


class UnavailableStepExecutor(StepExecutor):
    def execute(self, step: PlanStep) -> None:
        raise NotImplementedError(
            "Step execution is not implemented yet. " f"Cannot execute step {step.sequence}: {step.description}"
        )
