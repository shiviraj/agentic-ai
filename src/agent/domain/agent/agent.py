from abc import ABC, abstractmethod

from agent.domain.agent.agent_result import AgentResult
from agent.domain.agent.agent_role import AgentRole
from agent.domain.task.task import Task


class Agent(ABC):
    @property
    @abstractmethod
    def role(self) -> AgentRole:
        """Which job this agent does. The Manager uses it to find the agent."""

    @abstractmethod
    def run(self, task: Task) -> AgentResult:
        """Do the work for the task and report back.

        Must not change the task's status. The Manager does that.
        """
