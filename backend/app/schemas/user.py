from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SkillResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    experience_years: int = 0
    avatar_file_id: Optional[int] = None
    resume_file_id: Optional[int] = None
    user_role: str = "user"
    is_active: bool = True
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    skills: list[SkillResponse] = []

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    bio: Optional[str] = Field(None, max_length=2000)
    github_url: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    portfolio_url: Optional[str] = Field(None, max_length=255)
    experience_years: Optional[int] = Field(None, ge=0, le=100)


class PublicUserResponse(BaseModel):
    full_name: str
    bio: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    experience_years: int = 0
    avatar_file_id: Optional[int] = None
    resume_file_id: Optional[int] = None
    is_active: bool = True
    last_login_at: Optional[datetime] = None
    skills: list[SkillResponse] = []

    model_config = {"from_attributes": True}


class UserSkillsUpdateRequest(BaseModel):
    skill_ids: list[int]
