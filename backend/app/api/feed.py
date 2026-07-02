from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.project import ProjectResponse
from app.services.recommendation import RecommendationService
from app.core.redis import cache_get, cache_set, CacheKeys

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def get_feed(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cache_key = CacheKeys.feed(limit, offset)
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached
    service = RecommendationService(db)
    projects = await service.get_feed(user, offset=offset, limit=limit)

    data = [p.model_dump(mode="json") for p in projects]
    
    await cache_set(cache_key, data, ttl=60)
    
    return data