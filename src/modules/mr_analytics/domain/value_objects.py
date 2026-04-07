import datetime
import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Comment:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    author: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    body: str = ""
    resolvable: bool = False


@dataclass
class Approval:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    approver: str = ""
    approved_at: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class ReviewRound:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    round_number: int = 0
    started_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    completed_at: Optional[datetime.datetime] = None
