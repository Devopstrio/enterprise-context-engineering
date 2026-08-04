from __future__ import annotations

import hashlib
import time
from typing import Any, cast


class ContextCache:
    """Caches assembled context windows."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, dict[str, Any]] = {}
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

    def _generate_key(self, session_id: str, user_input: str, system_prompt: str) -> str:
        data = f"{session_id}:{user_input}:{system_prompt}".encode()
        return hashlib.sha256(data).hexdigest()

    def cache_context(self, cache_key: str, assembled_context: dict[str, Any], ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        self._cache[cache_key] = {
            "data": assembled_context,
            "expires_at": time.time() + ttl,
        }

    def get_cached_context(self, cache_key: str) -> dict[str, Any] | None:
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() < entry["expires_at"]:
                self._stats["hits"] += 1
                return cast(dict[str, Any], entry["data"])
            else:
                self.invalidate(cache_key)
                self._stats["evictions"] += 1

        self._stats["misses"] += 1
        return None

    def invalidate(self, cache_key: str) -> None:
        if cache_key in self._cache:
            del self._cache[cache_key]

    def get_cache_stats(self) -> dict[str, Any]:
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "size": len(self._cache),
        }
