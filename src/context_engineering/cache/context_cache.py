import time
from typing import Dict, Any, Optional
import hashlib
import json

class ContextCache:
    """Caches assembled context windows."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

    def _generate_key(self, session_id: str, user_input: str, system_prompt: str) -> str:
        data = f"{session_id}:{user_input}:{system_prompt}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def cache_context(self, cache_key: str, assembled_context: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        self._cache[cache_key] = {
            "data": assembled_context,
            "expires_at": time.time() + ttl
        }

    def get_cached_context(self, cache_key: str) -> Optional[Dict[str, Any]]:
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() < entry["expires_at"]:
                self._stats["hits"] += 1
                return entry["data"]
            else:
                self.invalidate(cache_key)
                self._stats["evictions"] += 1
        
        self._stats["misses"] += 1
        return None

    def invalidate(self, cache_key: str) -> None:
        if cache_key in self._cache:
            del self._cache[cache_key]

    def get_cache_stats(self) -> Dict[str, Any]:
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "size": len(self._cache)
        }
