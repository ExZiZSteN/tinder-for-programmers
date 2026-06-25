from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.match import Match
from app.repositories.base import BaseRepository
from app.models.project import Project
from app.models.match import MatchStatus
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

    async def get_with_project(self, match_id: int) -> Match | None:
        result = await self.db.execute(
            select(Match)
            .options(selectinload(Match.project))
            .where(Match.id == match_id)
        )
        return result.scalar_one_or_none()

    async def is_participant(self, match_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(Match)
            .join(Match.project)
            .where(Match.id == match_id,
                   or_(
                       Match.user_id == user_id,
                       Project.owner_id == user_id,
                    ),
                )
        )
        return result.scalar_one_or_none() is not None

    async def close_status(self, match: Match) -> Match:
        match.status = MatchStatus.CLOSED
        match.closed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return match
