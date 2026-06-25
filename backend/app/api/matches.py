from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.match import MatchResponse
from app.services.match import MatchService

router = APIRouter()


@router.get("", response_model=list[MatchResponse])
async def list_matches(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatchService(db)
    return await service.list_matches(user)


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatchService(db)
    return await service.get_by_id(user, match_id)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_match(
    match_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatchService(db)
    await service.close(user, match_id)
