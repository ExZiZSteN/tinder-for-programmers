from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def delete_by_hash(self, token_hash: str) -> None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        instance = result.scalar_one_or_none()
        if instance:
            await self.db.delete(instance)
            await self.db.commit()
    async def delete_expired(self) -> int:
        """Удалить все истёкшие токены (для cron-задачи).
        
        Returns:
            Количество удалённых токенов.
        """
        from sqlalchemy import delete
        
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            delete(RefreshToken)
            .where(RefreshToken.expires_at < now)
            .returning(RefreshToken.id)
        )
        return len(result.scalars().all())
    
    async def get_active_by_family(self, family_id: UUID) -> list[RefreshToken]:
        """Получить все АКТИВНЫЕ (не revoked, не expired) токены в семье."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked == False,  # noqa: E712
                RefreshToken.expires_at > now,
            )
        )
        return list(result.scalars().all())
    
    async def create(
            self,
            user_id: int,
            token_hash: str,
            family_id: UUID,
            expires_at: datetime | None = None,
        ) -> RefreshToken:
            """Создать новый refresh-токен.

            Args:
                user_id: ID пользователя.
                token_hash: SHA-256 хеш токена.
                family_id: UUID семейства (одинаковый для всех ротаций).
                expires_at: Срок действия. По умолчанию — 7 дней.
            """
            if expires_at is None:
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)

            return await super().create(
                user_id=user_id,
                token_hash=token_hash,
                family_id=family_id,
                expires_at=expires_at,
                revoked=False,
            )
    
    async def revoke_by_hash(self, token_hash: str) -> bool:
        """Отозвать токен по хешу (установить revoked=True).
        
        Returns:
            True если токен был найден и отозван, False если не найден.
        """
        result = await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked=True)
            .returning(RefreshToken.id)
        )
        return result.scalar_one_or_none() is not None

    async def revoke_token(self, token: RefreshToken) -> RefreshToken:
        """Отозвать конкретный токен (установить revoked=True).
        
        Args:
            token: Объект RefreshToken.
        
        Returns:
            Обновлённый объект с revoked=True.
        """
        return await self.update(token, revoked=True)

    async def revoke_family(self, family_id: UUID) -> int:
        """Отозвать ВСЕ токены в семействе (для reuse detection).
        
        Вызывается, когда обнаружено использование уже отозванного токена.
        Это инвалидирует все активные сессии пользователя.
        
        Args:
            family_id: UUID семейства.
        
        Returns:
            Количество отозванных токенов.
        """
        result = await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked == False,  # noqa: E712
            )
            .values(revoked=True)
            .returning(RefreshToken.id)
        )
        return len(result.scalars().all())