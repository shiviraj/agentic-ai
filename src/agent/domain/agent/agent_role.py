from enum import Enum


class AgentRole(str, Enum):
    ANALYSER = "ANALYSER"
    PLANNER = "PLANNER"
    CODER = "CODER"
    REVIEWER = "REVIEWER"
    QA = "QA"
