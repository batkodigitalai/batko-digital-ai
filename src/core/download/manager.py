"""Universal download task manager without network implementation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.core.download.events import DownloadEvent, DownloadEventType
from src.core.download.models import DownloadJob, DownloadResult, DownloadStatus
from src.core.download.progress import DownloadProgress
from src.core.download.queue import DownloadQueue
from src.core.download.retry import RetryPolicy
from src.core.logging import get_logger
from src.core.storage import ProjectStorage

logger = get_logger(__name__)


class DownloadManager:
    """Create and manage download tasks without performing network downloads."""

    def __init__(
        self,
        storage: ProjectStorage,
        queue: DownloadQueue | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.storage = storage
        self.queue = queue or DownloadQueue()
        self.retry_policy = retry_policy or RetryPolicy()
        self._jobs: dict[str, DownloadJob] = {}
        self._events: list[DownloadEvent] = []

    def create_task(
        self,
        source: str,
        target: Path | str,
        file_type: str,
        priority: int = 100,
        job_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> DownloadJob:
        """Create a download task and enqueue it."""
        job = DownloadJob(
            id=job_id or str(uuid4()),
            source=source,
            target=Path(target),
            fileType=file_type,
            priority=priority,
            metadata=metadata or {},
        )
        self.prepare_target(job)
        self._jobs[job.id] = job
        self.queue.enqueue(job)
        logger.info("Created download task {}", job.id)
        return job

    def run_task(self, job_id: str) -> DownloadResult:
        """Mark a task as started and finished without downloading bytes."""
        job = self.get_task(job_id)
        if job.status is DownloadStatus.CANCELLED:
            return self._result(job, error="Task is cancelled")
        job.status = DownloadStatus.RUNNING
        self._emit(job.id, DownloadEventType.STARTED)
        job.progress = DownloadProgress(percent=100.0, remainingBytes=0, downloadedBytes=job.size_bytes or 0)
        job.status = DownloadStatus.FINISHED
        job.completed_at = datetime.now(timezone.utc)
        self._emit(job.id, DownloadEventType.FINISHED)
        logger.info("Finished download task {} without network transfer", job.id)
        return self._result(job)

    def cancel_task(self, job_id: str) -> DownloadJob:
        """Cancel a task."""
        job = self.get_task(job_id)
        job.status = DownloadStatus.CANCELLED
        job.completed_at = datetime.now(timezone.utc)
        self._emit(job.id, DownloadEventType.CANCELLED)
        logger.info("Cancelled download task {}", job.id)
        return job

    def pause_task(self, job_id: str) -> DownloadJob:
        """Pause a task."""
        job = self.get_task(job_id)
        job.status = DownloadStatus.PAUSED
        logger.info("Paused download task {}", job.id)
        return job

    def resume_task(self, job_id: str) -> DownloadJob:
        """Resume a paused task by returning it to pending status."""
        job = self.get_task(job_id)
        if job.status is DownloadStatus.PAUSED:
            job.status = DownloadStatus.PENDING
            self.queue.enqueue(job)
        logger.info("Resumed download task {}", job.id)
        return job

    def retry_task(self, job_id: str) -> DownloadJob:
        """Retry a task if the retry policy allows it."""
        job = self.get_task(job_id)
        if not self.retry_policy.can_retry(job):
            job.status = DownloadStatus.FAILED
            self._emit(job.id, DownloadEventType.FAILED, message="Retry limit reached")
            logger.info("Retry limit reached for download task {}", job.id)
            return job
        job.status = DownloadStatus.PENDING
        self.queue.retry(job)
        self._emit(
            job.id,
            DownloadEventType.RETRY,
            payload={"retryCount": job.retry_count, "nextDelay": self.retry_policy.next_delay(job)},
        )
        return job

    def update_progress(self, job_id: str, progress: DownloadProgress) -> DownloadJob:
        """Update task progress data."""
        job = self.get_task(job_id)
        job.progress = progress
        self._emit(job.id, DownloadEventType.PROGRESS, payload=progress.model_dump(mode="json"))
        logger.info("Updated progress for download task {} to {}%", job.id, progress.percent)
        return job

    def get_status(self, job_id: str) -> DownloadStatus:
        """Return task status."""
        return self.get_task(job_id).status

    def get_task(self, job_id: str) -> DownloadJob:
        """Return task by id."""
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"Unknown download task: {job_id}") from exc

    def get_events(self, job_id: str | None = None) -> list[DownloadEvent]:
        """Return emitted events."""
        if job_id is None:
            return list(self._events)
        return [event for event in self._events if event.job_id == job_id]

    def prepare_target(self, job: DownloadJob) -> Path:
        """Prepare target directories using existing storage conventions."""
        self.storage.ensure_project_directories()
        job.target.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Prepared target directory {}", job.target.parent)
        return job.target.parent

    def _emit(
        self,
        job_id: str,
        event_type: DownloadEventType,
        message: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> DownloadEvent:
        event = DownloadEvent(jobId=job_id, eventType=event_type, message=message, payload=payload or {})
        self._events.append(event)
        logger.info("Download event {} for job {}", event_type.value, job_id)
        return event

    @staticmethod
    def _result(job: DownloadJob, error: str | None = None) -> DownloadResult:
        return DownloadResult(
            jobId=job.id,
            status=job.status,
            target=job.target,
            sizeBytes=job.size_bytes,
            checksum=job.checksum,
            checksumType=job.checksum_type,
            error=error,
        )

