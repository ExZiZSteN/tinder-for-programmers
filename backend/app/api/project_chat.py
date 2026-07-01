from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.project_message import ProjectMessageResponse, ProjectMessageCreateRequest
from app.services.project_chat import ProjectChatService

router = APIRouter()


@router.get("/{project_id}/messages", response_model=list[ProjectMessageResponse])
async def get_project_chat_history(
    project_id: int,
    before_id: int | None = Query(None, description="ID последнего загруженного сообщения"),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectChatService(db)
    return await service.get_history(user, project_id, before_id=before_id, limit=limit)


@router.post("/{project_id}/messages", response_model=ProjectMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_project_message(
    project_id: int,
    body: ProjectMessageCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectChatService(db)
    return await service.send_message(user, project_id, body)