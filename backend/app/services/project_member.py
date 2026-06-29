from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, NotFoundException, BadRequestException
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project_member import ProjectMemberUpdateRequest, ProjectMemberResponse


class ProjectMemberService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_member_role(
        self,
        current_user: User,
        project_id: int,
        user_id: int,
        data: ProjectMemberUpdateRequest,
    ) -> ProjectMemberResponse:
        """Изменить роль участника проекта."""
        # Проверяем, что проект существует
        project = await self.db.get(Project, project_id)
        if not project:
            raise NotFoundException("Project not found")

        # Проверяем, что текущий пользователь — владелец
        if project.owner_id != current_user.id:
            raise ForbiddenException("Only the project owner can manage members")

        # Нельзя изменить роль владельца
        if user_id == project.owner_id:
            raise BadRequestException("Cannot change the owner's role")

        # Находим участника
        result = await self.db.execute(
            select(ProjectMember)
            .options(selectinload(ProjectMember.user))
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        member = result.scalars().one_or_none()
        
        if not member:
            raise NotFoundException("Member not found")

        # Обновляем роль
        member.role = data.role
        await self.db.commit()
        await self.db.refresh(member)

        return ProjectMemberResponse.model_validate(member)

    async def remove_member(
        self,
        current_user: User,
        project_id: int,
        user_id: int,
    ) -> None:
        """Исключить участника из проекта."""
        # Проверяем, что проект существует
        project = await self.db.get(Project, project_id)
        if not project:
            raise NotFoundException("Project not found")

        # Проверяем, что текущий пользователь — владелец
        if project.owner_id != current_user.id:
            raise ForbiddenException("Only the project owner can manage members")

        # Нельзя исключить владельца
        if user_id == project.owner_id:
            raise BadRequestException("Cannot remove the owner")

        # Находим участника
        result = await self.db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.is_active == True,
            )
        )
        member = result.scalars().one_or_none()
        
        if not member:
            raise NotFoundException("Member not found")

        # Помечаем как неактивного (soft delete)
        member.is_active = False
        from datetime import datetime, timezone
        member.left_at = datetime.now(timezone.utc)
        await self.db.commit()