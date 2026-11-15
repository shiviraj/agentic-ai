from agent.application.workflow.workflow import Workflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult


class ConversationWorkflow(Workflow):
    async def execute(self, data: WorkflowInput) -> WorkflowResult:
        return WorkflowResult("Skip call, it will execute in response service")
