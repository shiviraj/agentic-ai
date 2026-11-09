from agent.domain.task.task import Task

from agent.domain.agent.agent import Agent
from agent.domain.agent.agent_result import AgentResult
from agent.domain.agent.agent_role import AgentRole


class FakeAgent(Agent):
    """Returns pre-written results in order; repeats the last one when it runs out."""

    def __init__(
        self,
        role: AgentRole,
        results: list[AgentResult] | None = None,
        log: list[AgentRole] | None = None,
        error: Exception | None = None,
    ) -> None:
        self._role = role
        self._results = list(results or [AgentResult.done(f"{role.value} output")])
        self._log = log
        self._error = error
        self.calls = 0
        self.seen_feedback: list[str | None] = []

    @property
    def role(self) -> AgentRole:
        return self._role

    def run(self, task: Task) -> AgentResult:
        self.calls += 1
        self.seen_feedback.append(task.feedback)
        if self._log is not None:
            self._log.append(self._role)
        if self._error is not None:
            raise self._error
        if len(self._results) > 1:
            return self._results.pop(0)
        return self._results[0]
