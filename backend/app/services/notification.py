from datetime import datetime, timezone
from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.ws_manager import notification_manager
from app.models.notification import Notification
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.core.redis import cache_get, cache_set, cache_delete, CacheKeys

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(db, Notification)
        self.notif_repo = NotificationRepository(db)
        self.db = db

    async def list(self, user: User) -> NotificationListResponse:
        key = CacheKeys.notifications(user.id)

        cached = await cache_get(key)
        if cached:
            # Восстанавливаем из кэша (там лежит dict)
            return NotificationListResponse.model_validate(cached)

        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
        )

        notifications = list(result.scalars().all())

        unread = sum(1 for n in notifications if not n.is_read)

        response = NotificationListResponse(
            notifications=[NotificationResponse.model_validate(n) for n in notifications],
            unread_count=unread,
        )

        # Кэшируем как dict (Pydantic v2 совместимый)
        await cache_set(key, response.model_dump(mode="json"), ttl=10)

        return response


    async def mark_read(self, user: User, notification_id: int) -> NotificationResponse:
        notification = await self.notif_repo.mark_read(notification_id, user.id)
        if not notification:
            raise NotFoundException("Notification")
        await self.db.commit()
        await self.db.refresh(notification)
        await cache_delete(CacheKeys.notifications(user.id))
        await cache_delete(CacheKeys.unread_count(user.id))
        return NotificationResponse.model_validate(notification)

    async def create(
        self,
        user_id: int,
        type: str,
        title: str,
        body: str | None = None,
        payload: dict | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            payload=payload or {},
        )
        self.db.add(notification)
        await self.db.flush()

        await notification_manager.send_to_user(
            user_id,
            {
                "type": "notification",
                "notification": {
                    "id": notification.id,
                    "user_id": user_id,
                    "type": type,
                    "title": title,
                    "body": body,
                    "payload": payload or {},
                    "is_read": False,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )

        await cache_delete(CacheKeys.notifications(user_id))
        await cache_delete(CacheKeys.unread_count(user_id))
        return notification

