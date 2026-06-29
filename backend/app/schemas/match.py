from datetime import datetime
from typing import Optional
from app.models.match import MatchStatus
from pydantic import BaseModel

class MatchProjectOwnerResponse(BaseModel):
    id: int
    full_name: str
    avatar_file_id: Optional[int] = None
    
    model_config = {"from_attributes": True}


class MatchProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    owner: MatchProjectOwnerResponse
    
    model_config = {"from_attributes": True}


class MatchUserResponse(BaseModel):
    id: int
    full_name: str
    avatar_file_id: Optional[int] = None
    experience_years: Optional[int] = None
    
    model_config = {"from_attributes": True}

class MatchResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    swipe_id: int
    status: MatchStatus
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    project: Optional[MatchProjectResponse] = None
    user: Optional[MatchUserResponse] = None
    
    model_config = {"from_attributes": True}
