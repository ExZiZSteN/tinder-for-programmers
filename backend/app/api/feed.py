from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.project import ProjectResponse
from app.services.recommendation import RecommendationService

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def get_feed(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RecommendationService(db)
    return await service.get_feed(user, offset=offset, limit=limit)
