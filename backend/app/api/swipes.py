from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.redis import cache_get, cache_set, cache_delete_pattern, CacheKeys
from app.models.user import User
from app.schemas.swipe import SwipeCreateRequest, SwipeResponse, SwipeReviewRequest
from app.services.swipe import SwipeService

router = APIRouter()


@router.post("", response_model=SwipeResponse, status_code=status.HTTP_201_CREATED)
async def create_swipe(
    body: SwipeCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SwipeService(db)
    await cache_delete_pattern(CacheKeys.INBOX_ALL)
    await cache_delete_pattern(CacheKeys.MY_SWIPES_ALL)
    await cache_delete_pattern(CacheKeys.FEED_ALL)

    return await service.create(user, body)


@router.get("/inbox", response_model=list[SwipeResponse])
async def get_inbox(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cache_key = CacheKeys.inbox(user.id)
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached
    service = SwipeService(db)
    result = await service.get_inbox(user)
    data = [s.model_dump(mode="json") for s in result]
    await cache_set(cache_key, data, ttl=30)
    return data

@router.get("/my", response_model=list[SwipeResponse])
async def get_my_swipes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить все отклики, отправленные текущим пользователем."""
    service = SwipeService(db)
    return await service.get_my_swipes(user)

# этот endpoint всегда последний
@router.patch("/{swipe_id}/review")
async def review_swipe(
    swipe_id: int,
    body: SwipeReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SwipeService(db)
    await cache_delete_pattern(CacheKeys.INBOX_ALL)
    await cache_delete_pattern(CacheKeys.MY_SWIPES_ALL)
    await cache_delete_pattern(CacheKeys.FEED_ALL)
    return await service.review(user, swipe_id, body)
