from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileUploadRequest(BaseModel):
    original_name: str
    mime_type: str
    size_bytes: int


class FileUploadResponse(BaseModel):
    id: int
    upload_url: str
    original_name: str
    expires_in: int


class FileDownloadResponse(BaseModel):
    id: int
    owner_id: int
    original_name: str
    mime_type: str
    size_bytes: int
    download_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
