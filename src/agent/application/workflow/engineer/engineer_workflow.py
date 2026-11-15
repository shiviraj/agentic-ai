from agent.application.service.engineer_service import EngineerService
from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_registry import WorkflowRegistry
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class EngineerWorkflow(Workflow):
    def __init__(
        self,
        workflow_registry: WorkflowRegistry,
        engineer_service: EngineerService
    ):
        self._engineer_service = engineer_service
        self._workflow_registry = workflow_registry
        self._logger = Logger("EngineerWorkflow")

    async def execute(self, data: WorkflowInput) -> WorkflowResult:
        classification = self._engineer_service.execute(data)
        response = await self._workflow_registry.execute_workflow(classification.request_type, data)
        return response

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are the Engineer Agent, the primary request classification agent
        for an AI-powered Senior Backend Engineer system.

        Your responsibility is to understand the user's latest request,
        consider the relevant conversation history, and classify the request

        User request:
        {user_request.value}
        """
