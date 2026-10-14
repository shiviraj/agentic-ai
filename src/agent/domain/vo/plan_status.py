from enum import Enum


class PlanStatus(str, Enum):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
