"""Models for real OPENLANE auction detection."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class SelectorVersion(BaseModel):
    """Selector set for one supported OPENLANE page version."""

    url_patterns: list[str] = Field(default_factory=list, alias="urlPatterns")
    auction_markers: list[str] = Field(default_factory=list, alias="auctionMarkers")
    fields: dict[str, list[str]] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class SelectorConfig(BaseModel):
    """Root selector registry model."""

    versions: dict[str, SelectorVersion]


class SelectorCheck(BaseModel):
    """Result of checking one selector against the current page."""

    version: str
    group: str
    name: str
    selector: str
    count: int

    @property
    def exists(self) -> bool:
        """Return whether the selector exists on the page."""
        return self.count > 0


class SelectorValidationReport(BaseModel):
    """Selector validation report for one page."""

    selector_file: Path = Field(alias="selectorFile")
    active_version: str = Field(alias="activeVersion")
    checks: list[SelectorCheck] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    def existing_selectors(self) -> list[SelectorCheck]:
        """Return selectors present on the page."""
        return [check for check in self.checks if check.exists]

    def missing_selectors(self) -> list[SelectorCheck]:
        """Return selectors missing on the page."""
        return [check for check in self.checks if not check.exists]


class RealAuctionDetection(BaseModel):
    """Detected metadata for an already-open real OPENLANE auction page."""

    title: str
    auction_id: str = Field(alias="auctionId")
    reference: str | None = None
    url: str
    selector_version: str = Field(alias="selectorVersion")
    selector_report: SelectorValidationReport = Field(alias="selectorReport")

    model_config = {"populate_by_name": True}


class OpenLaneAuctionDetectionError(RuntimeError):
    """Raised when the active page is not a detectable OPENLANE auction."""

