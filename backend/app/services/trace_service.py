import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.app.config import settings

TRACES_DIR = Path(settings.BASE_DIR) / "logs" / "traces"


class TraceService:
    """
    Cryptographically verifiable and auditable trace logging service.
    Persists complete agentic DAG execution records, physics parameter dictionaries,
    latency breakdowns, and sensor geometries for post-mission intelligence audits.
    """

    def __init__(self, traces_dir: Optional[Path] = None):
        self.traces_dir = traces_dir or TRACES_DIR
        self.traces_dir.mkdir(parents=True, exist_ok=True)

    def _compute_integrity_hash(self, trace_data: Dict[str, Any]) -> str:
        serialized = json.dumps(trace_data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def save_trace(self, trace_id: str, trace_data: Dict[str, Any]) -> str:
        trace_copy = dict(trace_data)
        if "integrity_hash" not in trace_copy:
            trace_copy["integrity_hash"] = self._compute_integrity_hash(trace_data)
        trace_copy["persisted_at"] = datetime.now(timezone.utc).isoformat()
        
        file_path = self.traces_dir / f"{trace_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trace_copy, f, indent=2)
        return str(file_path)

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        file_path = self.traces_dir / f"{trace_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        traces = []
        if not self.traces_dir.exists():
            return []
        
        trace_files = sorted(self.traces_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for tf in trace_files[:limit]:
            try:
                with open(tf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                traces.append({
                    "trace_id": data.get("trace_id", tf.stem),
                    "task_type": data.get("task_type"),
                    "total_execution_time_ms": data.get("total_execution_time_ms"),
                    "timestamp": data.get("timestamp"),
                    "integrity_hash": data.get("integrity_hash", "")[:16] + "..." if data.get("integrity_hash") else None,
                    "tools_count": len(data.get("tools_executed", []))
                })
            except Exception:
                continue
        return traces


trace_service = TraceService()
