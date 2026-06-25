from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.match import Match
from app.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    def __init__(self, db: AsyncSession):
        super().__init__(Match, db)

    async def get_by_user_and_project(
        self, user_id: int, project_id: int
    ) -> Match | None:
        result = await self.db.execute(
            select(Match).where(
                Match.user_id == user_id,
                Match.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: int) -> Sequence[Match]:
        result = await self.db.execute(
            select(Match)
            .where(
                Match.user_id == user_id,
                Match.status == "active",
            )
            .order_by(Match.created_at.desc())
        )
        return result.scalars().all()

    async def get_active_by_project(self, project_id: int) -> Sequence[Match]:
        result = await self.db.execute(
            select(Match)
            .where(
                Match.project_id == project_id,
                Match.status == "active",
            )
        )
        return result.scalars().all()

    async def is_participant(self, match_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(Match)
            .join(Match.project)
            .where(Match.id == match_id)
        )
        match = result.scalar_one_or_none()
        if not match:
            return False
        return match.user_id == user_id or match.project.owner_id == user_id