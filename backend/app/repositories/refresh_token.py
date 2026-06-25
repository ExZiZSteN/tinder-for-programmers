from sqlalchemy import select

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db):
        super().__init__(db, RefreshToken)

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
