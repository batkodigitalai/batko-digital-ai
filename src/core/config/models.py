"""Pydantic models for application configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class LoggingConfig(BaseModel):
    """Logging configuration for loguru."""

    logs_dir: Path = Path("logs")
    level: str = "INFO"
    rotation: str = "1 MB"
    retention: str = "14 days"
    file_name: str = "auto_v4.log"


class StorageConfig(BaseModel):
    """Project storage paths used by the foundation layer."""

    data_dir: Path = Path("30_DATA")
    cars_dir: Path = Path("30_DATA/cars")
    raw_dir: Path = Path("30_DATA/raw")
    assets_dir: Path = Path("50_ASSETS/cars")
    output_dir: Path = Path("40_OUTPUT/generated")
    previews_dir: Path = Path("40_OUTPUT/previews")
    archive_dir: Path = Path("60_ARCHIVE/snapshots")


class BrowserConfig(BaseModel):
    """Browser automation configuration for Sprint 2 infrastructure."""

    browser_mode: str = "local"
    chrome_profile: Path = Path("profiles/chrome/default")
    chrome_cdp: str = "http://127.0.0.1:9222"
    headless: bool = True
    playwright_timeout: int = 30000
    download_timeout: int = 120000


class AppConfig(BaseModel):
    """Top-level BATKO_AUTO_V4 configuration."""

    project_name: str = "BATKO_AUTO_V4"
    version: str = "0.1.0"
    environment: str = "local"
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
