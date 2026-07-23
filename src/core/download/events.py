"""Download event models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class DownloadEventType(StrEnum):
    """Supported download events."""

    STARTED = "started"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    FAILED = "failed"
    RETRY = "retry"
    PROGRESS = "progress"


class DownloadEvent(BaseModel):
    """Event emitted by DownloadManager."""

    job_id: str = Field(alias="jobId")
    event_type: DownloadEventType = Field(alias="eventType")
    message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    payload: dict[str, object] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

