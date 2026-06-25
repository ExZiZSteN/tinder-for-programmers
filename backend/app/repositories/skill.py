from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.models.skill import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self, db: AsyncSession):
        super().__init__(Skill, db)
    
    async def get_by_name(self, name: str) -> Skill | None:
        result = await self.db.execute(
            select(Skill).where(Skill.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_names(self, names: list[str]) -> Sequence[Skill]:
        if not names:
            return []
        result = await self.db.execute(
            select(Skill).where(Skill.name.in_(names))
        )
        return result.scalars().all()

    async def find_or_create(self, name: str) -> Skill:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        try:
            return await self.create(name=name)
        except IntegrityError:
            await self.db.rollback()
            result = await self.get_by_name(name)
            if result is None:
                raise
            return result
    
