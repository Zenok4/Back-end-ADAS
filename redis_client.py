"""
Redis client singleton cho toàn bộ ứng dụng.

Sử dụng:
    from redis_client import redis_client
    redis_client.set("key", "value", ex=300)
    redis_client.get("key")
"""

import redis
from config import REDIS_CONFIG
from logger import logger


def _create_redis_client() -> redis.Redis:
    """Khởi tạo Redis connection pool và trả về client."""
    pool = redis.ConnectionPool(
        host=REDIS_CONFIG["host"],
        port=REDIS_CONFIG["port"],
        password=REDIS_CONFIG["password"],
        db=REDIS_CONFIG["db"],
        decode_responses=REDIS_CONFIG["decode_responses"],
        max_connections=50,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )
    return redis.Redis(connection_pool=pool)


redis_client: redis.Redis = _create_redis_client()


def test_redis_connection() -> dict:
    """Kiểm tra kết nối Redis, dùng trong /test-connection."""
    try:
        redis_client.ping()
        return {"status": "success", "message": "Redis connection successful!"}
    except redis.RedisError as e:
        logger.error(f"[REDIS] Connection failed: {e}")
        return {"status": "failed", "error": str(e)}
