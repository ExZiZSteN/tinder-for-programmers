from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SkillResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProjectMemberResponse(BaseModel):
    user_id: int
    role: str
    joined_at: Optional[datetime] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    description: str
    format: str
    payment_type: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    skills: list[SkillResponse] = []
    members: list[ProjectMemberResponse] = []

    model_config = {"from_attributes": True}


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    format: str = Field(default="remote", pattern=r"^(remote|office|hybrid)$")
    payment_type: str = Field(default="volunteer", pattern=r"^(volunteer|paid|equity)$")
    skill_ids: list[int] = []


class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    format: Optional[str] = Field(None, pattern=r"^(remote|office|hybrid)$")
    payment_type: Optional[str] = Field(None, pattern=r"^(volunteer|paid|equity)$")
    status: Optional[str] = Field(None, pattern=r"^(draft|open|closed|archived)$")
    skill_ids: Optional[list[int]] = None
