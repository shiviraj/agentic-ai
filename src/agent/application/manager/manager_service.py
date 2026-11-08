from collections.abc import Sequence

from agent.application.manager.retry_policy import RetryPolicy
from agent.application.port.user_interaction import UserInteraction
from agent.domain.agent.agent import Agent
from agent.domain.agent.agent_result import AgentResult, ResultStatus
from agent.domain.agent.agent_role import AgentRole
from agent.domain.task.task import Task
from agent.domain.task.task_repository import TaskRepository
from agent.domain.task.task_status import TaskStatus, is_terminal
from agent.shared.logger.logger import Logger

# Which agent works on a task in each status
ROLE_FOR_STATUS: dict[TaskStatus, AgentRole] = {
    TaskStatus.ANALYSING: AgentRole.ANALYSER,
    TaskStatus.PLANNING: AgentRole.PLANNER,
    TaskStatus.CODING: AgentRole.CODER,
    TaskStatus.REVIEWING: AgentRole.REVIEWER,
    TaskStatus.TESTING: AgentRole.QA,
}

# Where the task goes when the agent says DONE
NEXT_STATUS_ON_DONE: dict[TaskStatus, TaskStatus] = {
    TaskStatus.ANALYSING: TaskStatus.PLANNING,
    TaskStatus.PLANNING: TaskStatus.CODING,
    TaskStatus.CODING: TaskStatus.REVIEWING,
    TaskStatus.REVIEWING: TaskStatus.TESTING,
    TaskStatus.TESTING: TaskStatus.DONE,
}

# Statuses where REJECTED is allowed, and the name of their retry counter
REJECTION_LOOPS: dict[TaskStatus, str] = {
    TaskStatus.REVIEWING: "review",
    TaskStatus.TESTING: "qa",
}


class ManagerService:
    def __init__(
        self,
        agents: Sequence[Agent],
        repository: TaskRepository,
        user: UserInteraction,
        policy: RetryPolicy | None = None,
    ) -> None:
        self._agents: dict[AgentRole, Agent] = {}
        for agent in agents:
            if agent.role in self._agents:
                raise ValueError(f"Two agents registered for role {agent.role.value}")
            self._agents[agent.role] = agent
        self._repository = repository
        self._user = user
        self._policy = policy or RetryPolicy()
        self._logger = Logger("ManagerService")

    def run(self, task: Task) -> Task:
        """Drive the task until it is DONE or FAILED, then return it."""
        self._repository.save(task)
        steps = 0

        while not is_terminal(task.status):
            steps += 1
            if steps > self._policy.max_total_steps:
                self._fail(
                    task,
                    f"Stopped: more than {self._policy.max_total_steps} steps",
                )
                break
            self._step(task)
            self._repository.save(task)

        self._repository.save(task)
        return task

    # ---- one step -------------------------------------------------

    def _step(self, task: Task) -> None:
        role = ROLE_FOR_STATUS.get(task.status)
        if role is None:
            self._fail(task, f"No agent works on status {task.status.value}")
            return

        agent = self._agents.get(role)
        if agent is None:
            self._fail(task, f"No agent registered for role {role.value}")
            return

        self._logger.info(f"task {task.id.value}: running {role.value}")
        try:
            result = agent.run(task)
        except Exception as e:  # an agent bug must not crash the whole loop
            self._logger.error(f"agent {role.value} crashed")
            self._fail(task, f"{role.value} agent crashed: {e}")
            return

        self._apply(task, role, result)

    def _apply(self, task: Task, role: AgentRole, result: AgentResult) -> None:
        if result.status == ResultStatus.DONE:
            self._apply_done(task, result)
        elif result.status == ResultStatus.REJECTED:
            self._apply_rejected(task, role, result)
        elif result.status == ResultStatus.NEEDS_CLARIFICATION:
            self._apply_clarification(task, role, result)
        else:  # FAILED
            self._fail(task, f"{role.value} failed: {result.output}")

    # ---- what each result means -----------------------------------

    def _apply_done(self, task: Task, result: AgentResult) -> None:
        if task.status == TaskStatus.ANALYSING:
            task.attach_requirements(result.output)
        elif task.status == TaskStatus.PLANNING:
            task.attach_plan(result.output)
        elif task.status == TaskStatus.CODING:
            task.clear_feedback()  # the coder has used the feedback
        task.move_to(NEXT_STATUS_ON_DONE[task.status])

    def _apply_rejected(self, task: Task, role: AgentRole, result: AgentResult) -> None:
        loop_name = REJECTION_LOOPS.get(task.status)
        if loop_name is None:
            self._fail(task, f"{role.value} returned REJECTED, which is not allowed")
            return

        count = task.increment_retry(loop_name)
        limit = self._policy.limit_for(loop_name)
        if count > limit:
            self._fail(
                task,
                f"{loop_name} still failing after {limit} retries. Last feedback: {result.output}",
            )
            return

        task.set_feedback(result.output)
        task.move_to(TaskStatus.CODING)

    def _apply_clarification(self, task: Task, role: AgentRole, result: AgentResult) -> None:
        if task.status != TaskStatus.ANALYSING:
            self._fail(task, f"{role.value} asked for clarification, which is not allowed")
            return

        count = task.increment_retry("clarification")
        limit = self._policy.limit_for("clarification")
        if count > limit:
            self._fail(task, f"Task still unclear after {limit} rounds of questions")
            return

        task.move_to(TaskStatus.WAITING_FOR_USER)
        for question in result.questions:
            task.add_clarification(question, self._user.ask(question))
        task.move_to(TaskStatus.ANALYSING)

    # ---- helpers --------------------------------------------------

    def _fail(self, task: Task, reason: str) -> None:
        self._logger.error(f"task {task.id.value} failed: {reason}")
        task.fail(reason)
