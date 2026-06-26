from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.models.skill import Skill
from app.models.user_skill import UserSkill
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

    async def get_all_skills(self, *, limit: int = 100, offset: int = 0) -> Sequence[Skill]:
        result = await self.db.execute(
            select(Skill)
            .order_by(Skill.name.asc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_popular(self, limit: int = 20) -> list[dict]:
        result = await self.db.execute(
            select(
                Skill.id,
                Skill.name,
                func.count(UserSkill.user_id).label("count",)
            )
            .join(UserSkill, UserSkill.skill_id == Skill.id, isouter=True)
            .group_by(Skill.id, Skill.name)
            .order_by(func.count(UserSkill.user_id).desc(), Skill.name.asc())
            .limit(limit)
        )
        return [
            {"id" : row.id, "name" : row.name, "count": row.count}
            for row in result.all()
        ]

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
        
    async def search(self, query: str, limit: int = 20) -> Sequence[Skill]:
        result = await self.db.execute(
            select(Skill)
            .where(Skill.name.ilike(f"%{query}%"))
            .order_by(Skill.name.asc())
            .limit(limit)
        )
        return result.scalars().all()
    
