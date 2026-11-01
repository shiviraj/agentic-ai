from abc import ABC, abstractmethod

from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.prompt import Prompt


class ProposalCreator(ABC):

    @abstractmethod
    def create(
            self,
            prompt: Prompt,
            context: ProjectContext | None,
    ) -> list[PlanStep]:
        ...
