from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.skill import SkillResponse
from app.models.project import ProjectStatus



class MemberUserResponse(BaseModel):
    id: int
    full_name: str
    avatar_file_id: Optional[int] = None

    model_config = {"from_attributes": True}
class ProjectOwnerResponse(BaseModel):
    id: int
    full_name: str
    avatar_file_id: Optional[int] = None
    
    model_config = {"from_attributes": True}
class ProjectMemberResponse(BaseModel):
    user_id: int
    role: str
    joined_at: Optional[datetime] = None
    is_active: bool = True
    user: MemberUserResponse
    
    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    description: str
    format: str
    payment_type: str
    status: ProjectStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    skills: list[SkillResponse] = []
    members: list[ProjectMemberResponse] = []
    owner: Optional[ProjectOwnerResponse]
    model_config = {"from_attributes": True}


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    format: str = Field(default="remote", pattern=r"^(remote|office|hybrid)$")
    payment_type: str = Field(default="volunteer", pattern=r"^(volunteer|paid|equity)$")
    status: ProjectStatus = Field(
        default=ProjectStatus.OPEN,
        description="Статус проекта: draft/open/closed/archived"
    )
    skill_ids: list[int] = []


class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    format: Optional[str] = Field(None, pattern=r"^(remote|office|hybrid)$")
    payment_type: Optional[str] = Field(None, pattern=r"^(volunteer|paid|equity)$")
    status: Optional[ProjectStatus] = Field(None, pattern=r"^(draft|open|closed|archived)$")
    skill_ids: Optional[list[int]] = None
