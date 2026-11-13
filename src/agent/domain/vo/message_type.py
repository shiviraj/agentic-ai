from enum import Enum


class MessageType(str, Enum):
    TEXT = "TEXT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    AGENT_RESPONSE = "AGENT_RESPONSE"
