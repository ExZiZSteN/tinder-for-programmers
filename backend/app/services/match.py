from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.user import User
from app.models.match import MatchStatus
from app.repositories.match import MatchRepository
from app.schemas.match import MatchResponse


class MatchService:
    def __init__(self, db: AsyncSession):
        self.repo = MatchRepository(db)
        self.db = db

    async def list_matches(self, user: User) -> list[MatchResponse]:
        matches = await self.repo.get_by_user(user.id)
        return [MatchResponse.model_validate(m) for m in matches]

    async def get_by_id(self, user: User, match_id: int) -> MatchResponse:
        match = await self.repo.get_by_id(match_id)
        if not match:
            raise NotFoundException("Match")
        if match.user_id != user.id and match.project.owner_id != user.id:
            raise ForbiddenException("Not a participant of this match")
        return MatchResponse.model_validate(match)

    async def close(self, user: User, match_id: int) -> None:
        match = await self.repo.get_by_id(match_id)
        if not match:
            raise NotFoundException("Match")
        if match.user_id != user.id and match.project.owner_id != user.id:
            raise ForbiddenException("Not a participant of this match")
        if match.status != MatchStatus.ACTIVE:
            raise BadRequestException("Match is already closed")

        match = await self.repo.close_status(match)
        await self.db.commit()
