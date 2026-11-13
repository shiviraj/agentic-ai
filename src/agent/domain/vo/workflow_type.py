from enum import Enum


class WorkflowType(str, Enum):
    CONVERSATION = "CONVERSATION"
    QUERY = "QUERY"
    TASK = "TASK"
