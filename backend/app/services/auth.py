from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
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
        refresh_token, _ = create_refresh_token(subject=user.id)
        await self.refresh_token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
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
        refresh_token, _ = create_refresh_token(subject=user.id)
        await self.refresh_token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
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

        try:
            payload = decode_token(raw_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
            user_id = int(payload["sub"])
        except (ValueError, KeyError):
            await self.refresh_token_repo.delete(stored)
            raise UnauthorizedException("Invalid refresh token")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active or user.is_banned:
            await self.refresh_token_repo.delete(stored)
            raise UnauthorizedException("User not found or inactive")

        await self.refresh_token_repo.delete(stored)

        new_access = create_access_token(subject=user.id)
        new_refresh, _ = create_refresh_token(subject=user.id)
        await self.refresh_token_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh),
        )

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
        )

    async def logout(self, raw_token: str) -> None:
        await self.refresh_token_repo.delete_by_hash(hash_refresh_token(raw_token))
