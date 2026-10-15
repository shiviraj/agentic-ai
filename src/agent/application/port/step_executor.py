from agent.domain.entity.plan_step import PlanStep


class StepExecutor:
    def execute(self, step: PlanStep) -> None:
        ...
