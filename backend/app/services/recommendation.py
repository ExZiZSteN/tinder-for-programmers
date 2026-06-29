from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.swipe import Swipe
from app.models.user import User
from app.schemas.project import ProjectResponse


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_feed(self, user: User, offset: int = 0, limit: int = 20) -> list[ProjectResponse]:
        swiped_subquery = (
            select(Swipe.project_id)
            .where(Swipe.user_id == user.id)
            .subquery()
        )

        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.project_skills),
                selectinload(Project.members),
            )
            .where(
                Project.owner_id != user.id,
                Project.id.notin_(swiped_subquery),
            )
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        projects = list(result.scalars().all())
        return [ProjectResponse.model_validate(p) for p in projects]
