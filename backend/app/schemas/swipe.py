from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.swipe import SwipeStatus

class SwipeResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    message: Optional[str] = None
    status: SwipeStatus
    created_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SwipeCreateRequest(BaseModel):
    project_id: int
    message: Optional[str] = Field(None, max_length=1000)


class SwipeReviewRequest(BaseModel):
    status: str  # "approved" | "rejected"
