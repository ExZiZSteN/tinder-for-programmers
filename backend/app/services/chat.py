from typing import Optional, List
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
        self.db = db
        self.repo = MessageRepository(db)
        self.match_repo = MatchRepository(db)

    async def _verify_participant(self, user: User, match_id: int) -> Match:
        """Внутренний метод для проверки, является ли пользователь участником мэтча."""
        match = await self.match_repo.get_with_project(match_id)
        if not match:
            raise NotFoundException("Match")
        
        if match.user_id != user.id and match.project.owner_id != user.id:
            raise ForbiddenException("You are not a participant of this match")
        return match

    async def get_history(
        self, 
        user: User, 
        match_id: int, 
        before_id: Optional[int] = None, 
        limit: int = 50
    ) -> List[MessageResponse]:
        """Получение истории чата с cursor-based пагинацией и отметкой о прочтении."""

        await self._verify_participant(user, match_id)
        

        messages = await self.repo.get_history(match_id, before_id=before_id, limit=limit)
        

        await self.repo.mark_read(match_id, user.id)
        await self.db.commit()
        
        return [MessageResponse.model_validate(m) for m in messages]

    async def save_message(
        self, match_id: int, sender_id: int, content: str
    ) -> WSMessageOut:
        """Сохранение сообщения, пришедшего через WebSocket протокол."""
        msg = await self.repo.create_message(match_id, sender_id, content)
        await self.db.commit()
        

        return WSMessageOut.model_validate(msg)

    async def send_message(
        self, user: User, match_id: int, data: MessageCreateRequest
    ) -> MessageResponse:
        """Отправка сообщения через классический HTTP POST запрос."""

        await self._verify_participant(user, match_id)
        

        message = await self.repo.create_message(
            match_id=match_id, 
            sender_id=user.id, 
            content=data.content
        )
        await self.db.commit()
        
        return MessageResponse.model_validate(message)
        
    async def mark_match_as_read(self, user: User, match_id: int) -> int:
        """Отдельный сервис-метод для принудительного прочтения чата (например, при клике)."""
        await self._verify_participant(user, match_id)
        affected_rows = await self.repo.mark_read(match_id, user.id)
        await self.db.commit()
        return affected_rows
