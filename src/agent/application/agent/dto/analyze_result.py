from dataclasses import dataclass
from enum import Enum


class RequestCategory(str, Enum):
    QUERY = "query"
    TASK = "task"
    CONVERSATION = "conversation"


@dataclass
class AnalyzeUserRequestResult:
    category: RequestCategory
    response: str
