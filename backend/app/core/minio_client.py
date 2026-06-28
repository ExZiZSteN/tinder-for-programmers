from datetime import timedelta

from minio import Minio
from io import BytesIO
from app.core.config import settings

_REGION = "us-east-1"

_internal = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL,
    region=_REGION,
)

_external = Minio(
    settings.MINIO_EXTERNAL_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_USE_SSL,
    region=_REGION,
)


async def init_minio_bucket() -> None:
    if not _internal.bucket_exists(settings.MINIO_BUCKET):
        _internal.make_bucket(settings.MINIO_BUCKET)


def get_presigned_upload_url(object_name: str, expires_hours: int = 1) -> str:
    return _external.presigned_put_object(
        settings.MINIO_BUCKET,
        object_name,
        expires=timedelta(hours=expires_hours),
    )


def get_presigned_download_url(object_name: str, expires_hours: int = 24) -> str:
    return _external.presigned_get_object(
        settings.MINIO_BUCKET,
        object_name,
        expires=timedelta(hours=expires_hours),
    )

def upload_file_from_bytes(
        object_name: str,
        data: bytes,
        content_type: str = "/application/octet-stream",
) -> bool:
    try:
        file_data = BytesIO(data)
        _internal.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
            data=file_data,
            length=len(data),
            content_type=content_type,
        )
        return True
    except Exception as e:
        print(f"Error when uploading file to MinIO: {e}")
        return False

def delete_file(object_name: str) -> bool:
    try:
        _internal.remove_bucket(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
        )
        return True
    except Exception as e:
        print(f"Error when deleating file from MinIO: {e}")
        return False