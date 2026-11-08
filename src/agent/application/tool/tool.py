from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from agent.domain.vo.tool_result import ToolResult
from agent.domain.vo.tool_risk import ToolRisk

ArgsT = TypeVar("ArgsT")


class Tool(ABC, Generic[ArgsT]):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def display_name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def tool_risk(self) -> ToolRisk: ...

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, object]: ...

    @abstractmethod
    def display_arguments(self, arguments: ArgsT) -> str | None: ...

    @abstractmethod
    def execute(self, arguments: ArgsT) -> ToolResult: ...
