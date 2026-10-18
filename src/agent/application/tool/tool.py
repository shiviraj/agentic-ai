from abc import abstractmethod, ABC, abstractproperty
from typing import TypeVar, Generic

from agent.domain.vo.tool_result import ToolResult
from agent.domain.vo.tool_risk import ToolRisk

ArgsT = TypeVar("ArgsT")


class Tool(ABC, Generic[ArgsT]):
    @abstractproperty
    def name(self) -> str:
        ...

    @abstractproperty
    def display_name(self) -> str:
        ...

    @abstractproperty
    def description(self) -> str:
        ...

    @abstractproperty
    def tool_risk(self) -> ToolRisk:
        ...

    @abstractproperty
    def parameters_schema(self) -> dict[str, object]:
        ...

    @abstractmethod
    def display_arguments(self, arguments: ArgsT) -> str | None:
        ...

    @abstractmethod
    def execute(self, arguments: ArgsT) -> ToolResult:
        ...
