from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.swipe import SwipeStatus


class SwipeUserResponse(BaseModel):
    id: int
    full_name: str
    avatar_file_id: Optional[int] = None
    
    model_config = {"from_attributes": True}


class SwipeProjectResponse(BaseModel):
    id: int
    title: str
    owner: Optional[SwipeUserResponse] = None

    model_config = {"from_attributes": True}

class SwipeResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    message: Optional[str] = None
    status: SwipeStatus
    match_id: Optional[int] = None
    created_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    user: Optional[SwipeUserResponse] = None
    project: Optional[SwipeProjectResponse] = None
    model_config = {"from_attributes": True}


class SwipeCreateRequest(BaseModel):
    project_id: int
    message: Optional[str] = Field(None, max_length=1000)


class SwipeReviewRequest(BaseModel):
    status: str  # "approved" | "rejected"
