from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PullRequestStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"

class PullRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PullRequestStatus
    assigned_reviewer: list[str]
    createdAt: Optional[datetime] = None
    mergedAt: Optional[datetime] = None

class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PullRequestStatus