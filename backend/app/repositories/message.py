from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, db: AsyncSession):
        super().__init__(Message, db)

    async def get_history(
        self,
        match_id: int,
        *,
        before_id: int | None = None,
        limit: int = 50,
    ) -> Sequence[Message]:
        """Cursor-based пагинация для истории чата."""
        query = select(Message).where(Message.match_id == match_id)
        if before_id is not None:
            query = query.where(Message.id < before_id)
        query = query.order_by(Message.id.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def mark_read(self, match_id: int, user_id: int) -> int:
        from datetime import datetime, timezone
        
        result = await self.db.execute(
            select(Message).where(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read == False,  # noqa: E712
            )
        )
        messages = result.scalars().all()
        now = datetime.now(timezone.utc)
        for msg in messages:
            msg.is_read = True
            msg.read_at = now
        await self.db.flush()
        return len(messages)

    async def count_unread(self, match_id: int, user_id: int) -> int:
        result = await self.db.execute(
            select(Message).where(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read == False,  # noqa: E712
            )
        )
        return len(result.scalars().all())