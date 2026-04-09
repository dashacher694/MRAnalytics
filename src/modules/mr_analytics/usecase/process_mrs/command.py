from pydantic import BaseModel, Field
from typing import List

from src.modules.mr_analytics.infrastructure.dto import VCSMergeRequestData


class ProcessMergeRequestsCommand(BaseModel):
    mrs: List[VCSMergeRequestData] = Field(..., description="List of VCS MR data")
