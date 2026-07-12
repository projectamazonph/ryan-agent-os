from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis


class JobQueue:
    queue_name = "raos:jobs"

    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url

    async def enqueue(self, job_type: str, payload: dict[str, Any]) -> None:
        client = Redis.from_url(self.redis_url, decode_responses=True)
        try:
            await client.rpush(self.queue_name, json.dumps({"type": job_type, "payload": payload}))
        finally:
            await client.aclose()  # type: ignore[attr-defined]
