from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.match import Match
from app.models.message import Message
from app.models.user import User
from app.repositories.match import MatchRepository
from app.repositories.message import MessageRepository
from app.schemas.message import MessageResponse, WSMessageOut, MessageCreateRequest


class ChatService:
    def __init__(self, db: AsyncSession):
        self.repo = MessageRepository(db)
        self.db = db
        self.match_repo = MatchRepository(db)

    async def _verify_participant(self, user: User, match_id: int) -> Match:
        match = await self.match_repo.get_with_project(match_id)
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

    async def send_message(
            self, user: User,  match_id : int, data: MessageCreateRequest
    ) -> Message:
        
        match = await self.db.get(Match, match_id)
        if not match:
            raise NotFoundException("Match")
        if match.user_id != user.id and match.project.owner_id != user.id:
            raise ForbiddenException("You are not part of this match")
        
        message = Message(
            match_id=match_id,
            sender_id=user.id,
            contend=data.content,
        )

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        return message