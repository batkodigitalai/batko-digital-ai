"""Download data models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from src.core.download.progress import DownloadProgress


def utc_now() -> datetime:
    """Return a timezone-aware timestamp."""
    return datetime.now(timezone.utc)


class DownloadStatus(StrEnum):
    """Lifecycle states for a download task."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FINISHED = "finished"
    FAILED = "failed"


class DownloadJob(BaseModel):
    """Download task description without network implementation."""

    id: str
    source: str
    target: Path
    file_type: str = Field(alias="fileType")
    status: DownloadStatus = DownloadStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now, alias="createdAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    size_bytes: int | None = Field(default=None, alias="sizeBytes")
    checksum: str | None = None
    checksum_type: str | None = Field(default=None, alias="checksumType")
    priority: int = 100
    retry_count: int = Field(default=0, alias="retryCount")
    max_retries: int = Field(default=3, alias="maxRetries")
    progress: DownloadProgress = Field(default_factory=DownloadProgress)
    metadata: dict[str, str] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class DownloadResult(BaseModel):
    """Result of a download task lifecycle operation."""

    job_id: str = Field(alias="jobId")
    status: DownloadStatus
    target: Path
    size_bytes: int | None = Field(default=None, alias="sizeBytes")
    checksum: str | None = None
    checksum_type: str | None = Field(default=None, alias="checksumType")
    error: str | None = None
    finished_at: datetime = Field(default_factory=utc_now, alias="finishedAt")

    model_config = {"populate_by_name": True}

