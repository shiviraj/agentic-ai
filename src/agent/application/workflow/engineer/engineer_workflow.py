from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.agent.dto.engineer_agent_result import RequestType
from agent.domain.agent.engineer_agent import EngineerAgent
from agent.shared.logger.logger import Logger


class EngineerWorkflow(Workflow):
    def __init__(
        self,
        engineer_agent: EngineerAgent,
        conversation_service: ConversationService,
        conversation_context_service: ConversationContextService,
    ):
        self._engineer_agent = engineer_agent
        self._conversation_service = conversation_service
        self._conversation_context_service = conversation_context_service
        self._workflow_maps = {}
        self._logger = Logger("EngineerWorkflow")

    def register_workflow(self, request_type: RequestType, workflow: Workflow) -> "EngineerWorkflow":
        self._workflow_maps[request_type] = workflow
        return self

    def execute(self, data: WorkflowInput) -> WorkflowResult:
        context = self._conversation_context_service.get_context(data.conversation_id)
        self._conversation_service.add_user_message(data.conversation_id, data.user_request.value)

        with self._logger.status("Classifying user request..."):
            classification = self._engineer_agent.execute(context, data.user_request)

        self._conversation_service.add_agent_response(
            data.conversation_id, agent_name="EngineerAgent", response=classification
        )
        self._logger.status("Successfully classified user request")

        # response = self._workflow_maps.get(classification.request_type).execute(data)
        return classification
