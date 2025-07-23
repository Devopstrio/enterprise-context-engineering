import time
from typing import Dict, List, Any, Optional
import tiktoken

class MemoryManager:
    """Manages conversation turns and memory within token limits."""

    def __init__(self, max_turns: int, sliding_window_size: int):
        self.max_turns = max_turns
        self.sliding_window_size = sliding_window_size
        self._store: Dict[str, List[Dict[str, Any]]] = {}
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def store_turn(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self._store:
            self._store[session_id] = []
        
        token_count = len(self.tokenizer.encode(content))
        turn = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "token_count": token_count
        }
        
        self._store[session_id].append(turn)
        
        # Apply sliding window eviction
        if len(self._store[session_id]) > self.sliding_window_size:
            self._store[session_id] = self._store[session_id][-self.sliding_window_size:]

    def retrieve_memory(self, session_id: str, max_tokens: int) -> List[Dict[str, Any]]:
        """Retrieves turns within token budget (most recent first, returned in chronological order)."""
        if session_id not in self._store or not self._store[session_id]:
            return []

        turns = self._store[session_id]
        selected_turns = []
        current_tokens = 0

        # Traverse backwards (most recent first)
        for turn in reversed(turns):
            if current_tokens + turn["token_count"] <= max_tokens:
                selected_turns.insert(0, turn)
                current_tokens += turn["token_count"]
            else:
                break
                
        return selected_turns

    def clear_session(self, session_id: str) -> None:
        if session_id in self._store:
            del self._store[session_id]

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._store or not self._store[session_id]:
            return {"turn_count": 0, "total_tokens": 0, "oldest_timestamp": None, "newest_timestamp": None}

        turns = self._store[session_id]
        total_tokens = sum(turn["token_count"] for turn in turns)
        return {
            "turn_count": len(turns),
            "total_tokens": total_tokens,
            "oldest_timestamp": turns[0]["timestamp"],
            "newest_timestamp": turns[-1]["timestamp"]
        }
