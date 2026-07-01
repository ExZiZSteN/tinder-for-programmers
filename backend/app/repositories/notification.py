from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_unread(self, user_id: int, *, limit: int = 50) -> Sequence[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_read(self, notification_id: int, user_id: int) -> Notification | None:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            await self.db.flush()
        return notification