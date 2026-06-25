from sqlalchemy import select

from app.models.swipe import Swipe
from app.repositories.base import BaseRepository


class SwipeRepository(BaseRepository[Swipe]):
    def __init__(self, db):
        super().__init__(db, Swipe)

    async def get_by_project_and_user(self, project_id: int, user_id: int) -> Swipe | None:
        result = await self.db.execute(
            select(Swipe).where(
                Swipe.project_id == project_id,
                Swipe.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_inbox_by_owner(self, owner_id: int) -> list[Swipe]:
        from app.models.project import Project
        result = await self.db.execute(
            select(Swipe)
            .join(Project, Swipe.project_id == Project.id)
            .where(Project.owner_id == owner_id)
            .order_by(Swipe.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_with_project(self, swipe_id: int) -> Swipe | None:
        from sqlalchemy.orm import joinedload
        result = await self.db.execute(
            select(Swipe)
            .options(joinedload(Swipe.project))
            .where(Swipe.id == swipe_id)
        )
        return result.scalar_one_or_none()
