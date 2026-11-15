from collections.abc import Generator

import redis

from app.config import settings

redis_pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> Generator[redis.Redis, None, None]:
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        client.close()
