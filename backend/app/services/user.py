from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException
from app.models.skill import Skill
from app.models.user import User
from app.models.user_skill import UserSkill
from app.repositories.user import UserRepository
from app.schemas.user import PublicUserResponse, UserResponse, UserUpdateRequest
from app.models.file import File


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.db = db

    async def get_profile(self, user: User) -> UserResponse:
        user_with_skills = await self.user_repo.get_with_skills(user.id)
        if not user_with_skills:
            raise NotFoundException("User")
        return UserResponse.model_validate(user_with_skills)

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
        user = await self.user_repo.get_with_skills(user_id)
        if not user:
            raise NotFoundException("User")
        return PublicUserResponse.model_validate(user)

    async def update_skills(self, user: User, skill_ids: list[int]) -> UserResponse:
        user_with_skills = await self.user_repo.get_with_skills(user.id)
        if not user_with_skills:
            raise NotFoundException("User")

        existing_ids = {us.skill_id for us in user_with_skills.user_skills}
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

    async def set_avatar(self, user: User, file_id: int) -> UserResponse:
        file = await self.db.get(File, file_id)
        if not file:
            raise NotFoundException("File")
        if file.owner_id != user.id:
            raise ForbiddenException("File does not belong to you")
    
        user.avatar_file_id = file_id
        await self.db.commit()
        await self.db.refresh(user)

        return await self.get_profile(user)

    async def remove_avatar(self, user: User) -> UserResponse:
        user.avatar_file_id = None
        await self.db.commit()
        await self.db.refresh(user)
        return await self.get_profile(user)

    async def set_resume(self, user: User, file_id: int) -> UserResponse:
        file = await self.db.get(File, file_id)
        if not file:
            raise NotFoundException("File")
        if file.owner_id != user.id:
            raise ForbiddenException("File does not belong to you")
        user.resume_file_id = file_id
        await self.db.commit()
        await self.db.refresh(user)

        return await self.get_profile(user)
    
    async def remove_resume(self, user: User) -> UserResponse:
        user.resume_file_id = None
        await self.db.commit()
        await self.db.refresh(user)
        return await self.get_profile(user)