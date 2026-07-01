from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.project import Project
from app.models.user import User
from app.models.project_member import ProjectMember
from app.repositories.project import ProjectRepository
from app.repositories.project_message import ProjectMessageRepository
from app.schemas.project_message import ProjectMessageResponse, WSProjectMessageOut, ProjectMessageCreateRequest


class ProjectChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProjectMessageRepository(db)
        self.project_repo = ProjectRepository(db)

    async def _verify_participant(self, user: User, project_id: int) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")

        result = await self.db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user.id,
                ProjectMember.is_active == True,
            )
        )

        member = result.scalar_one_or_none()

        if not member:
            raise ForbiddenException("You are not a participant of this project")
        return project
    
    async def get_history(
            self,
            user: User,
            project_id: int,
            before_id: Optional[int] = None,
            limit: int = 50
    ) -> List[ProjectMessageResponse]:
        await self._verify_participant(user, project_id)
        messages = await self.repo.get_history(project_id=project_id, before_id=before_id, limit=limit)
        return [ProjectMessageResponse.model_validate(m) for m in messages]
    
    async def save_message(
            self, project_id: int, sender_id: int, content: str
    ) -> WSProjectMessageOut:
        message = await self.repo.create_message(project_id=project_id, sender_id=sender_id, content=content)
        await self.db.commit()
        return WSProjectMessageOut.model_validate(message)
    
    async def send_message(
            self, user: User, project_id: int, data: ProjectMessageCreateRequest
    ) -> ProjectMessageResponse:
        await self._verify_participant(user, project_id)
        message = await self.repo.create_message(
            project_id=project_id,
            sender_id=user.id,
            content=data.content
        )
        await self.db.commit()
        return ProjectMessageResponse.model_validate(message)