"""Priority/FIFO download queue."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from src.core.download.models import DownloadJob
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(order=True)
class _QueueItem:
    priority: int
    sequence: int
    job: DownloadJob = field(compare=False)


class DownloadQueue:
    """Queue that supports priority, FIFO ordering, and retry requeue."""

    def __init__(self) -> None:
        self._items: list[_QueueItem] = []
        self._sequence = 0

    def enqueue(self, job: DownloadJob, priority: int | None = None) -> None:
        """Add a job to the queue."""
        effective_priority = job.priority if priority is None else priority
        job.priority = effective_priority
        heapq.heappush(self._items, _QueueItem(effective_priority, self._sequence, job))
        self._sequence += 1
        logger.info("Queued download job {} with priority {}", job.id, effective_priority)

    def dequeue(self) -> DownloadJob | None:
        """Return the next job by priority, preserving FIFO for equal priority."""
        if not self._items:
            logger.info("Download queue is empty")
            return None
        item = heapq.heappop(self._items)
        logger.info("Dequeued download job {}", item.job.id)
        return item.job

    def retry(self, job: DownloadJob) -> None:
        """Requeue a job for retry."""
        job.retry_count += 1
        logger.info("Retrying download job {} attempt {}", job.id, job.retry_count)
        self.enqueue(job, priority=job.priority)

    def __len__(self) -> int:
        return len(self._items)

