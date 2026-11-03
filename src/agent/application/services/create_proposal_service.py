from agent.application.port.proposal_creator import ProposalCreator
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.prompt import Prompt
from agent.shared.logger.Logger import Logger


class CreateProposalService:
    def __init__(self, proposal_creator: ProposalCreator) -> None:
        self._proposal_creator = proposal_creator
        self._logger = Logger("CreateProposalService")

    def create(self, context: ProjectContext | None, prompt: Prompt) -> list[PlanStep]:
        self._logger.debug("Creating Proposal started...")
        result = self._proposal_creator.create(prompt, context)
        self._logger.debug("Creating Proposal started...")
        self._logger.info("Successfully created Proposal.", "green bold")
        return result
