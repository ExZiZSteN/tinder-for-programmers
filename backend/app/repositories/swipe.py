from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.swipe import Swipe
from app.repositories.base import BaseRepository
from app.models.project import Project

class SwipeRepository(BaseRepository[Swipe]):
    def __init__(self, db: AsyncSession):
        super().__init__(Swipe, db)

    async def get_by_user_and_project(self, user_id: int, project_id: int) -> Swipe | None:
        result = await self.db.execute(
            select(Swipe).where(Swipe.user_id == user_id, Swipe.project_id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_by_project(self, project_id: int) -> Sequence[Swipe]:
        result = await self.db.execute(
            select(Swipe).where(Swipe.project_id == project_id, Swipe.status == "pending")
        .order_by(Swipe.created_at.desc()))
        return result.scalars().all()
    
    async def get_unviewed_projects(self, user_id: int, limit: int = 20) -> set[int]:
        
        swiped_subq = (
            select(Swipe.project_id).where(Swipe.user_id == user_id).scalar_subquery()
        )

        result = await self.db.execute(
            select(Project.id).where(
                Project.status == "open",
                Project.id.notin_(swiped_subq),
                Project.owner_id != user_id,
                ).order_by(Project.created_at.desc()).limit(limit)

        )
        return list(result.scalars().all())

    async def set_status(self, swipe: Swipe, status: str) -> Swipe:
        swipe.status = status
        swipe.reviewed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return swipe