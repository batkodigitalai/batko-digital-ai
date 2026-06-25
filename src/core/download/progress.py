"""Download progress model."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class DownloadProgress(BaseModel):
    """Progress data prepared for future download implementations."""

    percent: float = 0.0
    eta_seconds: float | None = Field(default=None, alias="etaSeconds")
    speed_bytes_per_second: float | None = Field(default=None, alias="speedBytesPerSecond")
    remaining_bytes: int | None = Field(default=None, alias="remainingBytes")
    downloaded_bytes: int = Field(default=0, alias="downloadedBytes")
    total_bytes: int | None = Field(default=None, alias="totalBytes")

    model_config = {"populate_by_name": True}

    @field_validator("percent")
    @classmethod
    def validate_percent(cls, value: float) -> float:
        """Clamp progress into the 0-100 range."""
        if value < 0:
            return 0.0
        if value > 100:
            return 100.0
        return value

