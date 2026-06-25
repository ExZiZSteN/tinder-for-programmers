from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.repositories.base import BaseRepository
from app.models.user_skill import UserSkill
class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_with_skills(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).options(selectinload(User.skills).selectinload(UserSkill.skill)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self, *, limit: int = 100, offset: int = 0) -> Sequence[User]:
        result = await self.db.execute(
            select(User).where(User.is_active == True).limit(limit).offset(offset).order_by(User.created_at.desc())
        )
        return result.scalars().all()
