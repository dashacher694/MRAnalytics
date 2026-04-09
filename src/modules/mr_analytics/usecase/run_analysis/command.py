from dataclasses import dataclass


@dataclass
class RunAnalysisCommand:
    days: int = 30


@dataclass
class RunAnalysisResponse:
    status: str
    fetched_count: int
    processed_count: int
    processed_mrs: list
    message: str
