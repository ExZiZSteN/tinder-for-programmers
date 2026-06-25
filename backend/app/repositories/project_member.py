from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project_member import ProjectMember
from app.repositories.base import BaseRepository


class ProjectMemberRepository(BaseRepository[ProjectMember]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProjectMember, db)

    async def get_active_membership(
        self, project_id: int, user_id: int
    ) -> ProjectMember | None:
        result = await self.db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_active_team(
        self, project_id: int
    ) -> Sequence[ProjectMember]:
        result = await self.db.execute(
            select(ProjectMember)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.is_active == True,  # noqa: E712
            )
            .order_by(ProjectMember.joined_at)
        )
        return result.scalars().all()

    async def get_user_projects(
        self, user_id: int
    ) -> Sequence[ProjectMember]:
        result = await self.db.execute(
            select(ProjectMember)
            .where(
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,  # noqa: E712
            )
        )
        return result.scalars().all()