from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.models.skill import Skill
from app.models.user import User
from app.models.user_skill import UserSkill
from app.repositories.user import UserRepository
from app.schemas.user import PublicUserResponse, UserResponse, UserUpdateRequest


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.db = db

    async def get_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def update_profile(self, user: User, data: UserUpdateRequest) -> UserResponse:
        updates = data.model_dump(exclude_unset=True)

        if "email" in updates:
            existing = await self.user_repo.get_by_email(updates["email"])
            if existing and existing.id != user.id:
                raise ConflictException("Email alredy taken")
        if not updates:
            return UserResponse.model_validate(user)
        updated = await self.user_repo.update(user, **updates)
        await self.db.commit()
        return UserResponse.model_validate(updated)

    async def get_user_by_id(self, user_id: int) -> PublicUserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        return PublicUserResponse.model_validate(user)

    async def update_skills(self, user: User, skill_ids: list[int]) -> UserResponse:
        existing_ids = {us.skill_id for us in user.user_skills}
        new_ids = set(skill_ids)

        to_remove = existing_ids - new_ids
        to_add = new_ids - existing_ids

        if to_remove:
            await self.db.execute(
                delete(UserSkill).where(
                    UserSkill.user_id == user.id,
                    UserSkill.skill_id.in_(to_remove),
                )
            )

        if to_add:
            existing_skills = await self.db.execute(
                select(Skill).where(Skill.id.in_(to_add))
            )
            found_ids = {s.id for s in existing_skills.scalars().all()}
            missing = to_add - found_ids
            if missing:
                raise NotFoundException(f"Skills: {missing}")
            for skill_id in to_add:
                self.db.add(UserSkill(user_id=user.id, skill_id=skill_id))

        await self.db.commit()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)
