"""Generic retry policy for download tasks."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.download.models import DownloadJob


@dataclass(frozen=True)
class RetryPolicy:
    """Retry policy independent of any concrete downloader."""

    max_attempts: int = 3
    backoff_seconds: float = 1.0
    backoff_multiplier: float = 2.0

    def can_retry(self, job: DownloadJob) -> bool:
        """Return whether a job can be retried."""
        allowed_attempts = min(self.max_attempts, job.max_retries)
        return job.retry_count < allowed_attempts

    def next_delay(self, job: DownloadJob) -> float:
        """Return the next delay for the current retry count."""
        return self.backoff_seconds * (self.backoff_multiplier ** job.retry_count)

