from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    PublicUserResponse,
    UserResponse,
    UserSkillsUpdateRequest,
    UserUpdateRequest,
)
from app.services.user import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_profile(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update_profile(user, body)


@router.put("/me/skills", response_model=UserResponse)
async def update_my_skills(
    body: UserSkillsUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update_skills(user, body.skill_ids)


@router.get("/{user_id}", response_model=PublicUserResponse)
async def get_user(
    user_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_user_by_id(user_id)
