from enum import Enum


class RiskScore(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MRState(Enum):
    MERGED = "merged"
    OPEN = "open"
    CLOSED = "closed"
