from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
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
    return await service.create(user, body)


@router.get("/inbox", response_model=list[SwipeResponse])
async def get_inbox(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SwipeService(db)
    return await service.get_inbox(user)

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
    return await service.review(user, swipe_id, body)
