from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.ws_manager import notification_manager
from app.models.notification import Notification
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationListResponse, NotificationResponse


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(db, Notification)
        self.notif_repo = NotificationRepository(db)
        self.db = db

    async def list(self, user: User) -> NotificationListResponse:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
        )
        notifications = list(result.scalars().all())

        count_result = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user.id, Notification.is_read == False)
        )
        unread_count = count_result.scalar() or 0

        return NotificationListResponse(
            notifications=[NotificationResponse.model_validate(n) for n in notifications],
            unread_count=unread_count,
        )

    async def mark_read(self, user: User, notification_id: int) -> NotificationResponse:
        notification = self.notif_repo.mark_read(notification_id, user.id)
        if not notification:
            raise NotFoundException("Notification")
        await self.db.commit()
        await self.db.refresh(notification)
        return NotificationResponse.model_validate(notification)

    async def create(
        self,
        user_id: int,
        type: str,
        title: str,
        body: str | None = None,
        payload: dict | None = None,
    ) -> NotificationResponse:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            payload=payload or {},
        )
        self.db.add(notification)
        await self.db.flush()
        try:
            await notification_manager.send_to_user(
                user_id,
                {
                    "type": type,
                    "payload": payload or {},
                    "created_at": notification.created_at.isoformat() if notification.created_at else None,
                },
            )
        except Exception:
            pass
        await self.db.commit()
        await self.db.refresh(notification)
        return NotificationResponse.model_validate(notification)
