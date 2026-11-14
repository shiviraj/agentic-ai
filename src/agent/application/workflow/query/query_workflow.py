from agent.application.service.investigation_service import InvestigationService
from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.shared.logger.logger import Logger


class QueryWorkflow(Workflow):
    def __init__(self, investigation_service: InvestigationService):
        self._investigation_service = investigation_service
        self._logger = Logger("QueryWorkflow")

    async def execute(self, data: WorkflowInput) -> WorkflowResult:
        response = await self._investigation_service.investigate(data.conversation_id, data.user_request)
        self._logger.info("Successfully responded to user query")
        return WorkflowResult(content=response.content)
