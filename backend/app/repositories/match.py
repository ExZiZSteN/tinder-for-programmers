from sqlalchemy import select, or_

from app.models.match import Match
from app.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    def __init__(self, db):
        super().__init__(db, Match)

    async def get_by_user(self, user_id: int) -> list[Match]:
        from app.models.project import Project
        result = await self.db.execute(
            select(Match)
            .join(Project, Match.project_id == Project.id)
            .where(
                or_(
                    Match.user_id == user_id,
                    Project.owner_id == user_id,
                )
            )
            .order_by(Match.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_by_project_and_user(self, project_id: int, user_id: int) -> Match | None:
        result = await self.db.execute(
            select(Match).where(
                Match.project_id == project_id,
                Match.user_id == user_id,
                Match.status == "active",
            )
        )
        return result.scalar_one_or_none()
