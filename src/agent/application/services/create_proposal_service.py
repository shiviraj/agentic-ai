from agent.application.port.proposal_creator import ProposalCreator
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.prompt import Prompt


class CreateProposalService:
    def __init__(self, proposal_creator: ProposalCreator) -> None:
        self._proposal_creator = proposal_creator

    def create(self, context: ProjectContext | None, prompt: Prompt) -> list[PlanStep]:
        return self._proposal_creator.create(prompt, context)
