"""
SatQuery AI - Analysis Job Store
Thread-safe in-memory store for tracking asynchronous analysis execution state and progress.
"""

import time
import uuid
import threading
from dataclasses import dataclass, field, asdict


@dataclass
class AnalysisJob:
    job_id: str
    status: str  # 'queued', 'running', 'completed', 'failed'
    stage: str   # Current processing stage name
    progress_pct: int
    message: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    overlay_bytes: Optional[bytes] = None
    report_bytes: Optional[bytes] = None

    def model_dump(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("overlay_bytes", None)
        d.pop("report_bytes", None)
        return d

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class JobStore:
    def __init__(self, max_jobs: int = 200):
        self._jobs: Dict[str, AnalysisJob] = {}
        self._lock = threading.Lock()
        self._max_jobs = max_jobs

    def create_job(
        self,
        job_id: Optional[str] = None,
        task_hint: Optional[str] = None,
        initial_message: str = "Analysis queued..."
    ) -> AnalysisJob:
        with self._lock:
            jid = job_id or f"job_{uuid.uuid4().hex[:10]}"
            job = AnalysisJob(
                job_id=jid,
                status="queued",
                stage="queued",
                progress_pct=5,
                message=initial_message
            )
            self._jobs[jid] = job
            self._prune_old_jobs()
            return job

    def update_stage(self, job_id: str, stage: str, progress_pct: int, message: str):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = "running"
                job.stage = stage
                job.progress_pct = progress_pct
                job.message = message
                job.updated_at = time.time()

    def complete_job(
        self,
        job_id: str,
        result: Dict[str, Any],
        overlay_bytes: Optional[bytes] = None,
        report_bytes: Optional[bytes] = None
    ):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = "completed"
                job.stage = "completed"
                job.progress_pct = 100
                job.message = "Analysis completed successfully."
                job.result = result
                job.overlay_bytes = overlay_bytes
                job.report_bytes = report_bytes
                job.updated_at = time.time()

    def fail_job(self, job_id: str, error_message: str):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = "failed"
                job.stage = "failed"
                job.message = error_message
                job.error = error_message
                job.updated_at = time.time()

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        with self._lock:
            return self._jobs.get(job_id)

    def _prune_old_jobs(self):
        # Keeps store within max_jobs bounds
        if len(self._jobs) > self._max_jobs:
            sorted_keys = sorted(self._jobs.keys(), key=lambda k: self._jobs[k].created_at)
            for k in sorted_keys[:20]:
                self._jobs.pop(k, None)


job_store = JobStore()
