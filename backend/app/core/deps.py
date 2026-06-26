from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import User
from app.core.database import async_session
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token, expected_type="access")
    user_id = int(payload["sub"])
    user_repo = UserRepository(db)

    user = await user_repo.get(user_id)
    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("User is inactive")
    if user.is_banned:
        raise UnauthorizedException("User is banned")

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.user_role != "admin":
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    return current_user