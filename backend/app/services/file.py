import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.minio_client import get_presigned_download_url, get_presigned_upload_url
from app.models.file import File
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.file import FileDownloadResponse, FileUploadResponse


class FileService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(db, File)
        self.db = db

    async def prepare_upload(
        self,
        user: User,
        original_name: str,
        mime_type: str,
        size_bytes: int,
    ) -> FileUploadResponse:
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        file = await self.repo.create(
            owner_id=user.id,
            filename=unique_name,
            original_name=original_name,
            path=unique_name,
            size_bytes=size_bytes,
            mime_type=mime_type,
        )
        upload_url = get_presigned_upload_url(unique_name, expires_hours=1)
        return FileUploadResponse(
            id=file.id,
            upload_url=upload_url,
            original_name=original_name,
            expires_in=3600,
        )

    async def get_download(self, user: User, file_id: int) -> FileDownloadResponse:
        file = await self.repo.get_by_id(file_id)
        if not file:
            raise NotFoundException("File")
        if file.owner_id != user.id:
            raise ForbiddenException("You do not have access to this file")
        download_url = get_presigned_download_url(file.path, expires_hours=24)
        return FileDownloadResponse(
            id=file.id,
            owner_id=file.owner_id,
            original_name=file.original_name,
            mime_type=file.mime_type,
            size_bytes=file.size_bytes,
            download_url=download_url,
            created_at=file.created_at,
        )
