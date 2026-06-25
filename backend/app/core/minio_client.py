from datetime import timedelta

from minio import Minio

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
