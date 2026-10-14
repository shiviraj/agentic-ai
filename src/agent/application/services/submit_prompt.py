from agent.domain.aggregate.agent_task import AgentTask
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.submit_prompt_result import SubmitPromptResult
from agent.domain.vo.task_id import TaskId


class SubmitPrompt:
    def execute(self, prompt: Prompt) -> SubmitPromptResult:
        task = AgentTask(id=TaskId.generate(), prompt=prompt)
        return SubmitPromptResult(task_id=task.id, status=task.status)
