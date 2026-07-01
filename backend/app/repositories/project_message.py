from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project_message import ProjectMessage
from app.repositories.base import BaseRepository


class ProjectMessageRepository(BaseRepository[ProjectMessage]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectMessage, db)

    async def get_history(
        self,
        project_id: int,
        *,
        before_id: int | None = None,
        limit: int = 50,
    ) -> Sequence[ProjectMessage]:
        query = select(ProjectMessage).where(ProjectMessage.project_id == project_id)
        if before_id is not None:
            query = query.where(ProjectMessage.id < before_id)
        query = query.order_by(ProjectMessage.id.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_message(self, project_id: int, sender_id: int, content: str) -> ProjectMessage:
        return await self.create(project_id=project_id, sender_id=sender_id, content=content)