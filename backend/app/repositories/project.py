from sqlalchemy import select

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db):
        super().__init__(db, Project)

    async def get_by_owner(self, owner_id: int, offset: int = 0, limit: int = 20) -> list[Project]:
        result = await self.db.execute(
            select(Project)
            .where(Project.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_all(self, offset: int = 0, limit: int = 20) -> list[Project]:
        result = await self.db.execute(
            select(Project).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self.db.execute(select(Project))
        return len(result.scalars().all())
