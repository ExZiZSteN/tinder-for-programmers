from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.skill import SkillRepository
from app.schemas.user import SkillResponse

router = APIRouter()

@router.get("", response_model=list[SkillResponse])
async def list_skills(
    q: str | None = Query(None, max_length=100, description="Поиск по имени"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    repo = SkillRepository(db)
    if q:
        skills = await repo.search(q, limit=limit)
    else:
        skills = await repo.get_all_skills(offset=offset, limit=limit)
    return [SkillResponse.model_validate(s) for s in skills]

@router.get("/popular", response_model=list[dict])
async def popular_skills(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = SkillRepository(db)
    return await repo.get_popular(limit=limit)

@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    name: str = Query(min_length=1, max_length=100, description="Название навыка"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = SkillRepository(db)
    skill = await repo.find_or_create(name)
    return SkillResponse.model_validate(skill)