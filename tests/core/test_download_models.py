from pathlib import Path

from src.core.download import DownloadJob, DownloadProgress, DownloadResult, DownloadStatus


def test_download_job_defaults() -> None:
    job = DownloadJob(id="job-1", source="manual", target=Path("target/file.bin"), fileType="binary")

    assert job.status is DownloadStatus.PENDING
    assert job.retry_count == 0
    assert job.progress.percent == 0
    assert job.completed_at is None


def test_download_result_aliases() -> None:
    result = DownloadResult(jobId="job-1", status=DownloadStatus.FINISHED, target=Path("out.bin"), sizeBytes=10)

    assert result.job_id == "job-1"
    assert result.size_bytes == 10


def test_download_progress_clamps_percent() -> None:
    assert DownloadProgress(percent=-5).percent == 0
    assert DownloadProgress(percent=150).percent == 100
    assert DownloadProgress(percent=42.5).percent == 42.5

