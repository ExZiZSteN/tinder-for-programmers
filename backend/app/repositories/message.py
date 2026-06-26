from typing import Sequence
from sqlalchemy import select, update, func
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

    async def get_by_match(self, match_id: int, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.match_id == match_id)
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_message(self, match_id: int, sender_id: int, content: str) -> Message:
        return await self.create(match_id=match_id, sender_id=sender_id, content=content)

    async def mark_read(self, match_id: int, user_id: int) -> int:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            update(Message).where(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read == False,  # noqa: E712
            ).values(is_read=True, read_at=now).returning(Message.id)
        )
        return len(result.scalars().all())

    async def count_unread(self, match_id: int, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Message)
            .where(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read == False,
            )
        )
        return result.scalar_one()
