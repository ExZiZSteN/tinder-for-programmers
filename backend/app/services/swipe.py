from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.project import Project
from app.models.swipe import Swipe
from app.models.user import User
from app.repositories.match import MatchRepository
from app.repositories.project import ProjectRepository
from app.repositories.swipe import SwipeRepository
from app.schemas.match import MatchResponse
from app.schemas.swipe import SwipeCreateRequest, SwipeResponse, SwipeReviewRequest


class SwipeService:
    def __init__(self, db: AsyncSession):
        self.swipe_repo = SwipeRepository(db)
        self.project_repo = ProjectRepository(db)
        self.match_repo = MatchRepository(db)
        self.db = db

    async def create(self, user: User, data: SwipeCreateRequest) -> SwipeResponse:
        project = await self.project_repo.get_by_id(data.project_id)
        if not project:
            raise NotFoundException("Project")

        if project.owner_id == user.id:
            raise BadRequestException("Cannot swipe on your own project")

        existing = await self.swipe_repo.get_by_project_and_user(
            project_id=data.project_id, user_id=user.id
        )
        if existing:
            raise BadRequestException("Already swiped on this project")

        swipe = await self.swipe_repo.create(
            user_id=user.id,
            project_id=data.project_id,
            message=data.message,
        )
        return SwipeResponse.model_validate(swipe)

    async def get_inbox(self, user: User) -> list[SwipeResponse]:
        swipes = await self.swipe_repo.get_inbox_by_owner(user.id)
        return [SwipeResponse.model_validate(s) for s in swipes]

    async def review(self, user: User, swipe_id: int, data: SwipeReviewRequest) -> SwipeResponse | MatchResponse:
        swipe = await self.swipe_repo.get_by_id_with_project(swipe_id)
        if not swipe:
            raise NotFoundException("Swipe")

        if swipe.project.owner_id != user.id:
            raise ForbiddenException("Only the project owner can review swipes")

        if swipe.status != "pending":
            raise BadRequestException("Swipe has already been reviewed")

        swipe.status = data.status
        swipe.reviewed_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(swipe)

        if data.status == "approved":
            existing = await self.match_repo.get_active_by_project_and_user(
                project_id=swipe.project_id,
                user_id=swipe.user_id,
            )
            if existing:
                return MatchResponse.model_validate(existing)

            match = await self.match_repo.create(
                user_id=swipe.user_id,
                project_id=swipe.project_id,
                swipe_id=swipe.id,
            )
            return MatchResponse.model_validate(match)

        return SwipeResponse.model_validate(swipe)
