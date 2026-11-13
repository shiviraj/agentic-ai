from dataclasses import dataclass
from enum import Enum


class RequestType(str, Enum):
    CONVERSATION = "CONVERSATION"
    QUERY = "QUERY"
    TASK = "TASK"


@dataclass(frozen=True)
class EngineerAgentResult:
    request_type: RequestType
    summary: str
