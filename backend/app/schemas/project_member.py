from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectMemberUpdateRequest(BaseModel):
    role: str = Field(..., pattern="^(owner|developer|teamlead|member)$")


class ProjectMemberResponse(BaseModel):
    user_id: int
    project_id: int
    role: str
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_active: bool
    
    model_config = {"from_attributes": True}