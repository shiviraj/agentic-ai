class ToolError(Exception):
    """Base class for every tool-related error in the domain."""


class ToolNotFoundError(ToolError):
    """The requested tool is not registered."""


class DuplicateToolError(ToolError):
    """Two tools tried to register under the same name."""


class ToolProviderError(ToolError):
    """A provider could not run a call (crash, broken protocol, closed connection)."""
