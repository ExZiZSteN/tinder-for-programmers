from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.file import File
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[File]):
    def __init__(self, db: AsyncSession):
        super().__init__(File, db)

    async def get_by_owner(
        self, owner_id: int, *, limit: int = 50
    ) -> Sequence[File]:
        result = await self.db.execute(
            select(File)
            .where(File.owner_id == owner_id)
            .order_by(File.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()