import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from fastapi.encoders import jsonable_encoder
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None

async def init_redis() -> redis.Redis:
    global redis_client
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding='utf-8',
        decode_responses=True,
    )
    try:
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Error with connecting Redis: {e}")
        raise
    return redis_client

async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None

def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis is not initialize. Call init_redis() for now.")
    return redis_client

async def cache_get(key: str):
    r = get_redis()
    value = await r.get(key)
    return json.loads(value) if value else None
    
async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    """Сохраняет значение в кэш с TTL (в секундах)."""
    try:
        r = get_redis()
        await r.set(key, json.dumps(jsonable_encoder(value)), ex=ttl)
    except Exception as e:
        logger.exception(f"Ошибка записи в Redis ({key}): {e}")


async def cache_delete(key: str) -> None:
    try:
        r = get_redis()
        await r.delete(key)
    except Exception as e:
        logger.exception(f"Error with deleating from Redis ({key}): {e}")

async def cache_delete_pattern(pattern: str) -> int:
    """Удаляет все ключи по паттерну. Возвращает количество удалённых."""
    try:
        r = get_redis()
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                deleted += await r.delete(*keys)
            if cursor == 0:
                break
        return deleted
    except Exception as e:
        logger.exception(f"Ошибка удаления по паттерну ({pattern}): {e}")
        return 0
    
class CacheKeys:
    """Централизованное хранение паттернов ключей кэша."""
    
    FEED = "feed:limit={limit}:offset={offset}"
    FEED_ALL = "feed:*"
    
    INBOX = "inbox:user={user_id}"
    INBOX_ALL = "inbox:*"
    
    MY_SWIPES = "my_swipes:user={user_id}"
    MY_SWIPES_ALL = "my_swipes:*"
    
    PUBLIC_PROFILE = "profile:user={user_id}"
    PUBLIC_PROFILE_ALL = "profile:*"
    
    SKILLS_LIST = "skills:list"
    
    UNREAD_COUNT = "unread:user={user_id}"
    UNREAD_ALL = "unread:*"
    
    ADMIN_STATS = "admin:stats"
    
    @staticmethod
    def feed(limit: int, offset: int) -> str:
        return CacheKeys.FEED.format(limit=limit, offset=offset)
    
    @staticmethod
    def inbox(user_id: int) -> str:
        return CacheKeys.INBOX.format(user_id=user_id)
    
    @staticmethod
    def my_swipes(user_id: int) -> str:
        return CacheKeys.MY_SWIPES.format(user_id=user_id)
    
    @staticmethod
    def public_profile(user_id: int) -> str:
        return CacheKeys.PUBLIC_PROFILE.format(user_id=user_id)

    @staticmethod
    def notifications(user_id: int) -> str:
        return CacheKeys.NOTIFICATIONS_LIST.format(user_id=user_id)
    
    @staticmethod
    def unread_count(user_id: int) -> str:
        return CacheKeys.UNREAD_COUNT.format(user_id=user_id)