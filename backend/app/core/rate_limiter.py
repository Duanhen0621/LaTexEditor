from __future__ import annotations

import hashlib

from redis.asyncio import Redis

from app.core.config import get_settings
from app.core.exceptions import RateLimitError

KEY_PREFIX = "rate_limit:login:"


def _build_key(identifier: str) -> str:
    """使用 IP 构建限流 key"""
    raw = f"{KEY_PREFIX}{identifier}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def check_login_rate_limit(redis: Redis, client_ip: str) -> None:
    """
    检查登录频率限制。
    在调用此函数后，调用方应在登录成功时调用 clear_login_rate_limit，
    在登录失败时不操作（计数器在 check 时已递增）。
    """
    settings = get_settings()
    key = _build_key(client_ip)
    max_attempts = settings.rate_limit_max_attempts
    window = settings.rate_limit_window_seconds

    # 递增计数器
    count = await redis.incr(key)

    if count == 1:
        # 首次失败，设置过期时间
        await redis.expire(key, window)

    if count > max_attempts:
        ttl = await redis.ttl(key)
        raise RateLimitError(
            message=f"登录尝试过于频繁，请 {ttl if ttl > 0 else window} 秒后再试"
        )


async def clear_login_rate_limit(redis: Redis, client_ip: str) -> None:
    """登录成功后清除限流计数"""
    key = _build_key(client_ip)
    await redis.delete(key)
