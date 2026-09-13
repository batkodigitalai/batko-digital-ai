from pathlib import Path

from src.core.download import DownloadEventType, DownloadManager, DownloadProgress, DownloadStatus, RetryPolicy
from src.core.storage import ProjectStorage


def make_manager(tmp_path: Path, retry_policy: RetryPolicy | None = None) -> DownloadManager:
    return DownloadManager(storage=ProjectStorage(project_root=tmp_path), retry_policy=retry_policy)


def test_download_manager_creates_task_and_prepares_target(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    target = tmp_path / "30_DATA" / "raw" / "file.bin"

    job = manager.create_task(source="manual", target=target, file_type="binary", job_id="job-1")

    assert job.id == "job-1"
    assert job.target == target
    assert target.parent.exists()
    assert manager.get_status("job-1") is DownloadStatus.PENDING


def test_download_manager_run_task_emits_events(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    job = manager.create_task(source="manual", target=tmp_path / "raw" / "file.bin", file_type="binary")

    result = manager.run_task(job.id)
    events = manager.get_events(job.id)

    assert result.status is DownloadStatus.FINISHED
    assert manager.get_status(job.id) is DownloadStatus.FINISHED
    assert [event.event_type for event in events] == [DownloadEventType.STARTED, DownloadEventType.FINISHED]


def test_download_manager_cancel_pause_resume(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    job = manager.create_task(source="manual", target=tmp_path / "raw" / "file.bin", file_type="binary")

    paused = manager.pause_task(job.id)
    assert paused.status is DownloadStatus.PAUSED

    resumed = manager.resume_task(job.id)
    assert resumed.status is DownloadStatus.PENDING

    cancelled = manager.cancel_task(job.id)
    assert cancelled.status is DownloadStatus.CANCELLED
    assert manager.get_events(job.id)[0].event_type is DownloadEventType.CANCELLED


def test_download_manager_updates_progress(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    job = manager.create_task(source="manual", target=tmp_path / "raw" / "file.bin", file_type="binary")
    progress = DownloadProgress(percent=25, etaSeconds=10, speedBytesPerSecond=100, remainingBytes=300)

    updated = manager.update_progress(job.id, progress)

    assert updated.progress.percent == 25
    assert manager.get_events(job.id)[0].event_type is DownloadEventType.PROGRESS


def test_download_manager_retry_respects_policy(tmp_path: Path) -> None:
    manager = make_manager(tmp_path, retry_policy=RetryPolicy(max_attempts=1))
    job = manager.create_task(source="manual", target=tmp_path / "raw" / "file.bin", file_type="binary")

    retried = manager.retry_task(job.id)
    failed = manager.retry_task(job.id)

    assert retried.retry_count == 1
    assert failed.status is DownloadStatus.FAILED
    assert manager.get_events(job.id)[-1].event_type is DownloadEventType.FAILED

