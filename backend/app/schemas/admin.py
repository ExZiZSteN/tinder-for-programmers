from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AdminUserResponse(BaseModel):
    """Схема для отображения пользователя в админке."""
    id: int
    email: str
    full_name: str
    user_role: str
    is_active: bool
    is_banned: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class AdminStatsResponse(BaseModel):
    """Схема для статистики в админке."""
    total_users: int
    total_projects: int
    total_matches: int
    total_skills: int
    banned_users: int
    active_projects: int