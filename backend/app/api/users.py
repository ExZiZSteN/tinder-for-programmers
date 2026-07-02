from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.redis import cache_get, cache_set, cache_delete, CacheKeys
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.user_skill import UserSkill
from app.models.skill import Skill
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

@router.get("/{user_id}/public")
async def get_public_profile(
        user_id: int,
        db: AsyncSession = Depends(get_db),
    ):
    """Публичный профиль пользователя (без email и пароля)."""
    cache_key = CacheKeys.public_profile(user_id)
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached
    
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.user_skills).selectinload(UserSkill.skill)
        )
        .where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = {
        "id": user.id,
        "full_name": user.full_name,
        "bio": user.bio,
        "github_url": user.github_url,
        "linkedin_url": user.linkedin_url,
        "portfolio_url": user.portfolio_url,
        "experience_years": user.experience_years,
        "avatar_file_id": user.avatar_file_id,
        "created_at": user.created_at,
        "skills": [
            {"id": us.skill.id, "name": us.skill.name}
            for us in user.user_skills
        ],
    }

    await cache_set(cache_key, data, ttl=300)
    return data

@router.post("/me/avatar", response_model=UserResponse)
async def set_avatar(
    file_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.set_avatar(user, file_id)

@router.delete("/me/avatar", response_model=UserResponse)
async def delete_avatar(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.remove_avatar(user)

@router.post("/me/resume", response_model=UserResponse)
async def set_resume(
    file_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.set_resume(user, file_id)

@router.delete("/me/resume", response_model=UserResponse)
async def delete_resume(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.remove_resume(user)