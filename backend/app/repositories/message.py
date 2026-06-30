from datetime import datetime, timezone
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
        """
        Cursor-based пагинация для истории чата (загрузка старых сообщений при скролле вверх).
        Возвращает сообщения, отсортированные от новых к более старым.
        """
        query = select(Message).where(Message.match_id == match_id)
        
        if before_id is not None:
            query = query.where(Message.id < before_id)
            
        query = query.order_by(Message.id.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_match(self, match_id: int, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        """
        Offset-based пагинация (классическая).
        Использует созданный композитный индекс (match_id, created_at).
        """
        query = (
            select(Message)
            .where(Message.match_id == match_id)
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_message(self, match_id: int, sender_id: int, content: str) -> Message:
        """Создание нового сообщения в чате."""
        return await self.create(match_id=match_id, sender_id=sender_id, content=content)

    async def mark_read(self, match_id: int, user_id: int) -> int:
        """
        Помечает прочитанными все входящие сообщения в конкретном мэтче.
        Возвращает количество прочитанных сообщений.
        """
        now = datetime.now(timezone.utc)
        

        stmt = (
            update(Message)
            .where(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read.is_(False),
            )
            .values(is_read=True, read_at=now)
            .returning(Message.id)
        )
        
        result = await self.db.execute(stmt)

        modified_ids = result.scalars().all()
        return len(modified_ids)

    async def count_unread(self, match_id: int, user_id: int) -> int:
        """Возвращает количество непрочитанных входящих сообщений в чате."""
        query = (
            select(func.count())
            .select_from(Message)
            .where(
                Message.match_id == match_id,
                Message.sender_id != user_id,
                Message.is_read.is_(False),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one()
