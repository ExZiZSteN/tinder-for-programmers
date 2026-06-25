from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.message import MessageResponse
from app.services.chat import ChatService

router = APIRouter()


@router.get("/{match_id}/messages", response_model=list[MessageResponse])
async def get_chat_history(
    match_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.get_history(user, match_id, offset=offset, limit=limit)
