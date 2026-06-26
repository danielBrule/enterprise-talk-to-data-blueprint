import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    trace_id: str
    rating: Literal[-1, 1]   # -1 = thumbs down, 1 = thumbs up
    comment: str | None = None


class FeedbackRecord(BaseModel):
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    rating: int
    comment: str | None
    user_role: str
