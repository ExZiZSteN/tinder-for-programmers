from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SwipeResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    message: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SwipeCreateRequest(BaseModel):
    project_id: int
    message: Optional[str] = None


class SwipeReviewRequest(BaseModel):
    status: str  # "approved" | "rejected"
