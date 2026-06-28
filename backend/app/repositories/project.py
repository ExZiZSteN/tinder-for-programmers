from typing import Sequence
from sqlalchemy import select, text, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.project import Project, ProjectStatus
from app.repositories.base import BaseRepository
from app.models.project_skill import ProjectSkill
from app.models.project_member import ProjectMember

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)
    
    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
            self,
            *,
            offset: int = 0,
            limit: int = 20,
            status: str | None = None,
            format: str | None = None,
            payment_type: str | None = None,
            skill_ids: list[int] | None = None,
        ) -> Sequence[Project]:

        query = (
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.project_skills),
                selectinload(Project.members),
            )
        )

        if status is None:
            query = query.where(Project.status != ProjectStatus.ARCHIVED)
        else:
            query = query.where(Project.status == status)
        if format:
            query = query.where(Project.format == format)
        if payment_type:
            query = query.where(Project.payment_type == payment_type)
        if skill_ids:
            query = query.where(
                exists().where(
                    (ProjectSkill.project_id == Project.id)
                    & (ProjectSkill.skill_id.in_(skill_ids))
                )
            )

        query = (
            query.order_by(Project.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_ids(self, ids: list[int]) -> Sequence[Project]:
        """Загрузить проекты по списку ID с relations."""
        if not ids:
            return []
        
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.project_skills),
                selectinload(Project.members),
            )
            .where(Project.id.in_(ids))
            .order_by(Project.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_project(self, user_id: int, *, offest: int = 0, limit: int = 50) -> Sequence[Project]:
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.project_skills),
                selectinload(Project.members),
            )
            .where(
                (Project.owner_id == user_id)
                | (
                    Project.id.in_(
                        select(ProjectMember.project_id).where(
                            ProjectMember.user_id == user_id,
                            ProjectMember.is_active == True,
                        )
                    )
                )
            )
            .order_by(Project.created_at.desc())
            .offset(offest)
            .limit(limit)
        )
        return result.scalars().all()

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
            select(Project).options(
                selectinload(Project.skills).selectinload(ProjectSkill.skill)
                ).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def search_by_title(self, query_text: str, *, limit: int = 20) -> Sequence[Project]:
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.project_skills),
                selectinload(Project.members),    
            )
            .where(Project.title.ilike(f"%{query_text}", escape="\\"))
            .order_by(text("similarity(title, :q) DESC"))
            .params(q=query_text).limit(limit)
        )
        return result.scalars().all()