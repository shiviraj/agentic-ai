from agent.application.workflow.conversation.conversation_workflow import ConversationWorkflow
from agent.application.workflow.query.query_workflow import QueryWorkflow
from agent.application.workflow.task.task_workflow import TaskWorkflow
from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult
from agent.domain.agent.dto.engineer_agent_result import RequestType
from agent.domain.errors import DataNotFoundError


class WorkflowRegistry:
    def __init__(
        self,
        conversation_workflow: ConversationWorkflow,
        query_workflow: QueryWorkflow,
        task_workflow: TaskWorkflow,
    ):
        self._workflow_maps: dict[RequestType, Workflow] = {
            RequestType.CONVERSATION: conversation_workflow,
            RequestType.QUERY: query_workflow,
            RequestType.TASK: task_workflow,
        }

    async def execute_workflow(self, request_type: RequestType, data: WorkflowInput) -> WorkflowResult:
        workflow = self._get_workflow(request_type=request_type)
        return await workflow.execute(data)

    def _get_workflow(self, request_type: RequestType) -> Workflow:
        workflow = self._workflow_maps.get(request_type)
        if workflow is None:
            raise DataNotFoundError(f"Workflow not found for {request_type.value}")
        return workflow
