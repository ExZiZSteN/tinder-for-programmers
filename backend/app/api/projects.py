from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis import cache_delete_pattern, cache_delete, CacheKeys
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.services.project import ProjectService
from app.schemas.project_member import (
    ProjectMemberUpdateRequest,
    ProjectMemberResponse,
)
from app.services.project import ProjectService
from app.services.project_member import ProjectMemberService
router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    status: str | None = Query(
        None,
        description="Фильтр по статутсу: draft/open/closed/archived. По умолчанию - open"
    ),
    format: str | None = Query(
        None,
        description="Фильтр по формату: remote/office/hybrid"
    ),
    payment_type: str | None = Query(
        None,
        description="Фильтр по типу оплаты: volunteer/paid/equity",
    ),
    skill_ids: list[int] | None = Query(
        None,
        description="Фильтр по навыкам (ID). Проект должен иметь хотя бы один из указанных навыков",
    ),
):
    service = ProjectService(db)
    return await service.list_projects(
        offset=offset, 
        limit=limit,
        status=status,
        format=format,
        payment_type=payment_type,
        skill_ids=skill_ids,
    )

@router.get("/my", response_model=list[ProjectResponse])
async def my_project(
    offest: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    return await service.get_my_projects(user,offset=offest,limit=limit)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await cache_delete_pattern(CacheKeys.FEED_ALL)
    return await service.create(user, body)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.get_by_id(project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    body: ProjectUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await cache_delete_pattern(CacheKeys.FEED_ALL)
    await cache_delete(CacheKeys.public_profile(user.id))
    return await service.update(user, project_id, body)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await cache_delete_pattern(CacheKeys.FEED_ALL)
    await service.delete(user, project_id)

@router.post("/{project_id}/restore", response_model=ProjectResponse)
async def resotre_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ProjectService(db)
    return await service.restore(user, project_id)

@router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: int,
    user_id: int,
    body: ProjectMemberUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Изменить роль участника проекта (только для владельца)."""
    service = ProjectMemberService(db)
    return await service.update_member_role(current_user, project_id, user_id, body)


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Исключить участника из проекта (только для владельца)."""
    service = ProjectMemberService(db)
    await service.remove_member(current_user, project_id, user_id)