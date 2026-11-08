from agent.application.services.execute_plan import ExecutePlan
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.shared.logger.logger import Logger


class ExecutePlanWorkflow:
    def __init__(
        self,
        execute_plan: ExecutePlan,
    ) -> None:
        self._execute_plan = execute_plan
        self._logger = Logger("ExecutePlanWorkflow")

    def execute(self, plan: ImplementationPlan) -> None:
        self._execute_plan.execute(plan)
