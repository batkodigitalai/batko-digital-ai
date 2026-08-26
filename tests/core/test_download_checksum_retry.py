from pathlib import Path

from src.core.download import DownloadJob, RetryPolicy, calculate_crc32, calculate_md5, calculate_sha256


def test_checksum_utilities(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("batko-auto-v4", encoding="utf-8")

    assert calculate_sha256(file_path) == "09aa7babca748083f08f553183da72734a23a6de843abdfc54b4fc5bd5302fc9"
    assert calculate_md5(file_path) == "c584a9296da387fafa78b30bf12438fb"
    assert calculate_crc32(file_path) == "25046bfb"


def test_retry_policy() -> None:
    job = DownloadJob(id="job-1", source="manual", target=Path("target.bin"), fileType="binary", maxRetries=3)
    policy = RetryPolicy(max_attempts=2, backoff_seconds=2, backoff_multiplier=3)

    assert policy.can_retry(job) is True
    assert policy.next_delay(job) == 2

    job.retry_count = 1
    assert policy.can_retry(job) is True
    assert policy.next_delay(job) == 6

    job.retry_count = 2
    assert policy.can_retry(job) is False
