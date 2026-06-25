from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)
    
    async def get_by_owner(self, owner_id, *, limit: int = 50, offset: int = 0) -> Sequence[Project]:
        result = await self.db.execute(
            select(Project).where(Project.owner_id == owner_id).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def get_open_projects(self, *, limit: int = 20, offset: int = 0) -> Sequence[Project]:
        result = await self.db.execute(
            select(Project).where(Project.status == "open").order_by(Project.created_at.desc())
            .limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def get_with_skills(self, project_id: int) -> Project | None:
        result = await self.db.execute(
            select(Project).options(selectinload(Project.skills)).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def search_by_title(self, query_text: str, *, limit: int = 20) -> Sequence[Project]:
        result = await self.db.execute(
            select(Project).where(Project.title.ilike(f"%{query_text}")).limit(limit)
        )
        return result.scalars().all()