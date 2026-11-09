from agent.domain.vo.prompt import Prompt

from agent.application.service.analyze_requirement_service import AnalyzeRequirementService
from agent.application.service.create_proposal_service import CreateProposalService
from agent.application.service.discover_context_service import DiscoverContextService
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.shared.logger.logger import Logger


class CreatePlanWorkflow:
    def __init__(
        self,
        analyze_requirement_service: AnalyzeRequirementService,
        discover_context_service: DiscoverContextService,
        create_proposal_service: CreateProposalService,
    ) -> None:
        self._analyze_requirement_service = analyze_requirement_service
        self._discover_context_service = discover_context_service
        self._create_proposal_service = create_proposal_service
        self._logger = Logger("CreatePlanWorkflow")

    def execute(self, prompt: Prompt) -> ImplementationPlan:
        analysis_result = self._analyze_requirement_service.analyze(prompt)
        context = self._discover_context_service.discover(analysis_result, prompt)
        steps = self._create_proposal_service.create(context=context, prompt=prompt)

        plan = ImplementationPlan.create(steps=steps)
        text = "Implementation plan created\n"
        for step in plan.steps:
            text += f"  {step.sequence}. {step.title}\n"
        self._logger.info(text)
        return plan
