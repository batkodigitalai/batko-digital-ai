from pathlib import Path

from src.core.download import DownloadJob, DownloadQueue


def make_job(job_id: str, priority: int = 100) -> DownloadJob:
    return DownloadJob(id=job_id, source="manual", target=Path(f"{job_id}.bin"), fileType="binary", priority=priority)


def test_download_queue_preserves_fifo_for_same_priority() -> None:
    queue = DownloadQueue()
    first = make_job("first")
    second = make_job("second")

    queue.enqueue(first)
    queue.enqueue(second)

    assert queue.dequeue() is first
    assert queue.dequeue() is second
    assert queue.dequeue() is None


def test_download_queue_uses_priority() -> None:
    queue = DownloadQueue()
    low = make_job("low", priority=100)
    high = make_job("high", priority=1)

    queue.enqueue(low)
    queue.enqueue(high)

    assert queue.dequeue() is high
    assert queue.dequeue() is low


def test_download_queue_retry_increments_retry_count() -> None:
    queue = DownloadQueue()
    job = make_job("retry")

    queue.retry(job)

    assert job.retry_count == 1
    assert len(queue) == 1

