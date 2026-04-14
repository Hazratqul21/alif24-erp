import json
from typing import Optional, Any
from redis.asyncio import Redis
from app.config import settings

_redis: Optional[Redis] = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Optional[Any]:
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_set(key: str, value: Any, expire: int = 300):
    r = await get_redis()
    await r.set(key, json.dumps(value, default=str), ex=expire)


async def cache_delete(key: str):
    r = await get_redis()
    await r.delete(key)


async def cache_delete_pattern(pattern: str):
    r = await get_redis()
    async for key in r.scan_iter(match=pattern):
        await r.delete(key)
