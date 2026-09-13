"""Data models for OPENLANE page snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return a timezone-aware timestamp."""
    return datetime.now(timezone.utc)


class PageMetadata(BaseModel):
    """Basic metadata for an already-open page."""

    url: str
    title: str
    timestamp: datetime = Field(default_factory=utc_now)
    page_id: str | None = Field(default=None, alias="pageId")
    auction_id: str | None = Field(default=None, alias="auctionId")

    model_config = {"populate_by_name": True}


class PageSnapshot(BaseModel):
    """Files produced by a page snapshot."""

    snapshot_id: str = Field(alias="snapshotId")
    directory: Path
    metadata: PageMetadata
    html_path: Path = Field(alias="htmlPath")
    title_path: Path = Field(alias="titlePath")
    url_path: Path = Field(alias="urlPath")
    screenshot_path: Path = Field(alias="screenshotPath")

    model_config = {"populate_by_name": True}

