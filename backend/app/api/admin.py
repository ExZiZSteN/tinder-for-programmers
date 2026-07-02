from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.core.deps import get_current_admin, get_db
from app.models.user import User
from app.models.project import Project
from app.models.skill import Skill
from app.models.match import Match
from app.schemas.admin import AdminUserResponse, AdminStatsResponse
from app.schemas.project import ProjectResponse
from app.core.redis import cache_get, cache_set, cache_delete, CacheKeys

router = APIRouter()

@router.get("/stats", response_model=AdminStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    cache_key = CacheKeys.ADMIN_STATS
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    total_users = await db.scalar(select(func.count(User.id)))
    total_projects = await db.scalar(select(func.count(Project.id)))
    total_matches = await db.scalar(select(func.count(Match.id)))
    total_skills = await db.scalar(select(func.count(Skill.id)))
    banned_users = await db.scalar(select(func.count(User.id)).where(User.is_banned == True))
    active_projects = await db.scalar(select(func.count(Project.id)).where(Project.status == "open"))
    
    data = {
        "total_users": total_users or 0,
        "total_projects": total_projects or 0,
        "total_matches": total_matches or 0,
        "total_skills": total_skills or 0,
        "banned_users": banned_users or 0,
        "active_projects": active_projects or 0,
    }
    await cache_set(cache_key, data, ttl=30)
    return data


@router.get("/users")
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = None,
    role: str | None = None,
    is_banned: bool | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(User)
    
    if search:
        query = query.where(
            (User.full_name.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%"))
        )
    if role:
        query = query.where(User.user_role == role)
    if is_banned is not None:
        query = query.where(User.is_banned == is_banned)
    
    query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()
    
    total = await db.scalar(select(func.count(User.id)))
    
    return {
        "users": [AdminUserResponse.model_validate(u) for u in users],
        "total": total or 0,
    }

@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_banned = body.get("is_banned", True)
    await db.commit()
    await db.refresh(user)
    
    return AdminUserResponse.model_validate(user)

@router.patch("/users/{user_id}/role")
async def change_role(
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_role = body.get("role")
    if new_role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user.user_role = new_role
    await db.commit()
    await db.refresh(user)
    
    return AdminUserResponse.model_validate(user)

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    await db.commit()
    
    return {"message": "User deleted"}

@router.get("/projects")
async def list_projects(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    query = select(Project)
    if status:
        query = query.where(Project.status == status)
    
    query = query.offset(offset).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    
    total = await db.scalar(select(func.count(Project.id)))
    
    return {
        "projects": [ProjectResponse.model_validate(p) for p in projects],
        "total": total or 0,
    }

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.status = "archived"
    await db.commit()
    
    return {"message": "Project deleted"}

@router.get("/skills")
async def list_skills(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    should_cache = not search and offset == 0 and limit == 100
    
    if should_cache:
        cache_key = CacheKeys.SKILLS_LIST
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached
    

    query = select(Skill)
    if search:
        query = query.where(Skill.name.ilike(f"%{search}%"))
    
    query = query.offset(offset).limit(limit).order_by(Skill.name)
    result = await db.execute(query)
    skills = result.scalars().all()
    
    total = await db.scalar(select(func.count(Skill.id)))
    
    data = {
        "skills": [{"id": s.id, "name": s.name} for s in skills],
        "total": total or 0,
    }
    
    if should_cache:
        await cache_set(cache_key, data, ttl=600)  # 10 минут
    
    return data


@router.post("/skills")
async def create_skill(
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    skill = Skill(name=name)
    db.add(skill)
    await db.commit()
    await db.refresh(skill)

    await cache_delete(CacheKeys.SKILLS_LIST)
    
    return {"id": skill.id, "name": skill.name}


@router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    skill = await db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    await db.delete(skill)
    await db.commit()
    
    await cache_delete(CacheKeys.SKILLS_LIST)
    
    return {"message": "Skill deleted"}