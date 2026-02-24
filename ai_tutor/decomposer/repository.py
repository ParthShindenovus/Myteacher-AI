import json
from typing import Any

import redis
from django.conf import settings


class StateRepository:
    def __init__(self) -> None:
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def save(self, session_id: str, value: dict[str, Any]) -> None:
        self.client.set(f"session:{session_id}:decomposer", json.dumps(value))

    def load(self, session_id: str) -> dict[str, Any] | None:
        raw = self.client.get(f"session:{session_id}:decomposer")
        return json.loads(raw) if raw else None
