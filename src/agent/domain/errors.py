class DomainError(Exception):
    """Base class for all errors raised by our own code."""


class InvalidStatusTransitionError(DomainError):
    """A task tried to move to a status it is not allowed to reach."""


class TaskNotFoundError(DomainError):
    """No task exists with the given id."""


class LlmUnavailableError(DomainError):
    """The LLM could not be reached or returned an unusable answer."""


class InvalidAgentOutputError(DomainError):
    """An agent's LLM answer could not be understood or failed validation."""


class WorkspaceError(DomainError):
    """A file operation in the workspace failed."""


class UnsafePathError(WorkspaceError):
    """A path is not allowed (outside the workspace, hidden, wrong type...)."""
