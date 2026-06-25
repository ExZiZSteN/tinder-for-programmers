from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.match import Match
from app.models.message import Message
from app.models.user import User
from app.repositories.message import MessageRepository
from app.schemas.message import MessageResponse, WSMessageOut


class ChatService:
    def __init__(self, db: AsyncSession):
        self.repo = MessageRepository(db)
        self.db = db

    async def _verify_participant(self, user: User, match_id: int) -> Match:
        result = await self.db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        if not match:
            raise NotFoundException("Match")
        if match.user_id != user.id and match.project.owner_id != user.id:
            raise ForbiddenException("Not a participant of this match")
        return match

    async def get_history(
        self, user: User, match_id: int, offset: int = 0, limit: int = 50
    ) -> list[MessageResponse]:
        await self._verify_participant(user, match_id)
        messages = await self.repo.get_by_match(match_id, offset=offset, limit=limit)
        return [MessageResponse.model_validate(m) for m in messages]

    async def save_message(
        self, match_id: int, sender_id: int, content: str
    ) -> WSMessageOut:
        msg = await self.repo.create_message(match_id, sender_id, content)
        return WSMessageOut(
            id=msg.id,
            match_id=msg.match_id,
            sender_id=msg.sender_id,
            content=msg.content,
            created_at=msg.created_at,
        )
