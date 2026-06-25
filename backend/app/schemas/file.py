from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FileUploadRequest(BaseModel):
    original_name: str
    mime_type: str
    size_bytes: int


class FileUploadResponse(BaseModel):
    id: int
    owner_id: int
    upload_url: str
    original_name: str
    expires_in: int


class FileDownloadResponse(BaseModel):
    id: int
    owner_id: int
    original_name: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^[^/\\]+\.[a-zA-Z0-9]+$",
        description="Имя файла без путей",
    )
    mime_type: str = Field(
        pattern=r"^[a-z]+/[a-z0-9\-\+\.]+$",
        description="MIME-типб например image/png",
    )
    size_bytes: int = Field(
        gt=0, le=10 * 1024 * 1024, # до 10 МБ
    )
    download_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
