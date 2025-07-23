import structlog
from typing import Dict, Any, List

class ContextAuditLogger:
    """Logs context assembly decisions."""

    def __init__(self):
        self.logger = structlog.get_logger("context_audit")
        self._events: List[Dict[str, Any]] = []

    def log_assembly_event(self, session_id: str, event_type: str, details: Dict[str, Any]) -> None:
        event = {
            "session_id": session_id,
            "event_type": event_type,
            "details": details
        }
        self._events.append(event)
        self.logger.info("audit_event", **event)

    def log_budget_allocation(self, session_id: str, allocation: Any) -> None:
        self.log_assembly_event(session_id, "BUDGET_ALLOCATED", allocation.model_dump() if hasattr(allocation, "model_dump") else allocation)

    def log_compression_event(self, session_id: str, compression_result: Any) -> None:
        self.log_assembly_event(session_id, "CONTEXT_COMPRESSED", compression_result.model_dump() if hasattr(compression_result, "model_dump") else compression_result)

    def log_cache_event(self, session_id: str, event_type: str, cache_key: str) -> None:
        self.log_assembly_event(session_id, event_type, {"cache_key": cache_key})

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._events[-limit:]
