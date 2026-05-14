import logging
from typing import AsyncIterator

import redis.asyncio as redis_async
from redis.asyncio import Redis

from app.config import settings

logger = logging.getLogger(__name__)


_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis_async.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
    return _redis_client


async def get_redis() -> AsyncIterator[Redis]:
    yield get_redis_client()


async def safe_get(key: str) -> str | None:
    try:
        return await get_redis_client().get(key)
    except Exception as exc:
        logger.warning("Redis GET failed for %s: %s", key, exc)
        return None


async def safe_set(key: str, value: str, ttl: int) -> None:
    try:
        await get_redis_client().set(key, value, ex=ttl)
    except Exception as exc:
        logger.warning("Redis SET failed for %s: %s", key, exc)


async def safe_delete(key: str) -> None:
    try:
        await get_redis_client().delete(key)
    except Exception as exc:
        logger.warning("Redis DEL failed for %s: %s", key, exc)


async def ping() -> bool:
    try:
        return bool(await get_redis_client().ping())
    except Exception as exc:
        logger.warning("Redis PING failed: %s", exc)
        return False
