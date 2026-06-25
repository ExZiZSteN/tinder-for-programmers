from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.project_skill import ProjectSkill
from app.models.skill import Skill
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.repo = ProjectRepository(db)
        self.db = db

    async def create(self, user: User, data: ProjectCreateRequest) -> ProjectResponse:
        project = await self.repo.create(
            owner_id=user.id,
            title=data.title,
            description=data.description,
            format=data.format,
            payment_type=data.payment_type,
        )

        self.db.add(ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role="owner",
        ))

        if data.skill_ids:
            await self._sync_skills(project, data.skill_ids)

        await self.db.commit()
        await self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    async def get_by_id(self, project_id: int) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project")
        return ProjectResponse.model_validate(project)

    async def update(self, user: User, project_id: int, data: ProjectUpdateRequest) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project")
        if project.owner_id != user.id:
            raise ForbiddenException("Only the owner can edit the project")

        updates = data.model_dump(exclude_unset=True, exclude={"skill_ids"})
        if updates:
            project = await self.repo.update(project, **updates)

        if data.skill_ids is not None:
            await self._sync_skills(project, data.skill_ids)

        await self.db.refresh(project)
        return ProjectResponse.model_validate(project)

    async def delete(self, user: User, project_id: int) -> None:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project")
        if project.owner_id != user.id:
            raise ForbiddenException("Only the owner can delete the project")

        await self.db.execute(
            delete(ProjectSkill).where(ProjectSkill.project_id == project.id)
        )
        await self.db.execute(
            delete(ProjectMember).where(ProjectMember.project_id == project.id)
        )
        await self.db.execute(
            delete(Project).where(Project.id == project.id)
        )
        await self.db.commit()

    async def list_projects(self, offset: int = 0, limit: int = 20) -> list[ProjectResponse]:
        projects = await self.repo.list_all(offset=offset, limit=limit)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def _sync_skills(self, project: Project, skill_ids: list[int]) -> None:
        existing_ids = {ps.skill_id for ps in project.project_skills}
        new_ids = set(skill_ids)

        to_remove = existing_ids - new_ids
        to_add = new_ids - existing_ids

        if to_remove:
            await self.db.execute(
                delete(ProjectSkill).where(
                    ProjectSkill.project_id == project.id,
                    ProjectSkill.skill_id.in_(to_remove),
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
                self.db.add(ProjectSkill(project_id=project.id, skill_id=skill_id))
        await self.db.flush()
