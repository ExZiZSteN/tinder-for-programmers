from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timezone, timedelta
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_refresh_token_with_family,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.refresh_token_repo = RefreshTokenRepository(db)

    async def register(self, email: str, password: str, full_name: str) -> TokenResponse:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException("Email already registered")

        user = await self.user_repo.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )

        access_token = create_access_token(subject=user.id)
        refresh_token, family_id = create_refresh_token(subject=user.id)
        await self.refresh_token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            family_id=family_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid credentials")

        access_token = create_access_token(subject=user.id)
        refresh_token, family_id = create_refresh_token(subject=user.id)
        await self.refresh_token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            family_id=family_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, raw_token: str) -> TokenResponse:
        token_hash = hash_refresh_token(raw_token)
        stored = await self.refresh_token_repo.get_by_hash(token_hash)
        if not stored:
            raise UnauthorizedException("Invalid refresh token")

        if stored.revoked:
            await self.refresh_token_repo.revoke_family(stored.family_id)
            raise UnauthorizedException("Token reuse detected")

        if stored.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedException("Refresh token expired")

        try:
            payload = decode_token(raw_token, expected_type="refresh")
            user_id = int(payload["sub"])
        except (ValueError, KeyError, TypeError):
            await self.refresh_token_repo.delete(stored)
            raise UnauthorizedException("Invalid refresh token")

        user = await self.user_repo.get(user_id)
        if not user or not user.is_active or user.is_banned:
            await self.refresh_token_repo.delete(stored)
            raise UnauthorizedException("User not found or inactive")

        await self.refresh_token_repo.revoke_token(stored)

        new_access = create_access_token(subject=user.id)
        new_refresh, new_family_id = create_refresh_token_with_family(subject=user.id, family_id=stored.family_id)
        await self.refresh_token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh),
            family_id=stored.family_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
        )

    async def logout(self, raw_token: str) -> None:
        await self.refresh_token_repo.revoke_by_hash(hash_refresh_token(raw_token))
