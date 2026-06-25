from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.file import FileDownloadResponse, FileUploadRequest, FileUploadResponse
from app.services.file import FileService

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    body: FileUploadRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    return await service.prepare_upload(
        user,
        original_name=body.original_name,
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
    )


@router.get("/{file_id}", response_model=FileDownloadResponse)
async def get_file(
    file_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    return await service.get_download(user, file_id)
