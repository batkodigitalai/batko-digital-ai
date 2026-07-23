"""Models for OPENLANE capture archives."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from src.openlane.reader import AuctionReadResult
from src.openlane.photos import PhotoManifest


class CaptureStatus(StrEnum):
    """Final capture status."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"


class ManifestFile(BaseModel):
    """One file recorded in a capture manifest."""

    path: str
    sha256: str
    size_bytes: int = Field(alias="sizeBytes")

    model_config = {"populate_by_name": True}


class CaptureManifest(BaseModel):
    """Manifest for one auction capture."""

    captured_at: datetime = Field(alias="capturedAt")
    app_version: str = Field(alias="appVersion")
    commit_hash: str | None = Field(default=None, alias="commitHash")
    status: CaptureStatus
    url: str
    auction_id: str | None = Field(default=None, alias="auctionId")
    files: list[ManifestFile] = Field(default_factory=list)
    missing_required: list[str] = Field(default_factory=list, alias="missingRequired")
    photo_total: int = Field(default=0, alias="photoTotal")
    photo_downloaded: int = Field(default=0, alias="photoDownloaded")
    photo_failed: int = Field(default=0, alias="photoFailed")

    model_config = {"populate_by_name": True}


class CaptureResult(BaseModel):
    """Result of one end-to-end auction capture."""

    capture_dir: Path = Field(alias="captureDir")
    source_dir: Path = Field(alias="sourceDir")
    manifest_path: Path = Field(alias="manifestPath")
    log_path: Path = Field(alias="logPath")
    manifest: CaptureManifest
    read_result: AuctionReadResult = Field(alias="readResult")
    photo_manifest: PhotoManifest | None = Field(default=None, alias="photoManifest")

    model_config = {"populate_by_name": True}
