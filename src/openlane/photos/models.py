"""Models for OPENLANE photo downloads."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return a timezone-aware timestamp."""
    return datetime.now(timezone.utc)


class PhotoDownloadStatus(StrEnum):
    """Result of one photo download attempt."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PhotoManifestItem(BaseModel):
    """One photo entry in photos.json."""

    order: int
    url: str
    local_file: str | None = Field(default=None, alias="localFile")
    sha256: str | None = None
    size_bytes: int | None = Field(default=None, alias="sizeBytes")
    result: PhotoDownloadStatus
    error: str | None = None

    model_config = {"populate_by_name": True}


class PhotoManifest(BaseModel):
    """Manifest for downloaded auction photos."""

    created_at: datetime = Field(default_factory=utc_now, alias="createdAt")
    total: int
    downloaded: int
    failed: int
    photos: list[PhotoManifestItem] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
