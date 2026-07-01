from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.message import MessageResponse, MessageCreateRequest
from app.services.chat import ChatService

router = APIRouter()


@router.get("/{match_id}/history", response_model=list[MessageResponse])
async def get_chat_history(
    match_id: int,
    before_id: int | None = Query(None, description="ID последнего загруженного сообщения"),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.get_history(user, match_id, before_id=before_id, limit=limit)


@router.post("/{match_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    match_id: int,
    body: MessageCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.send_message(user, match_id, body)


@router.post("/{match_id}/read")
async def mark_as_read(
    match_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    count = await service.mark_match_as_read(user, match_id)
    return {"read_count": count}