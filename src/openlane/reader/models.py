"""Models for OPENLANE reader validation and export."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from src.domain.models.car import Car
from src.openlane.downloader import PageSnapshot


class FieldRequirement(StrEnum):
    """Validation requirement level for an extracted field."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    UNKNOWN = "unknown"


class FieldValidation(BaseModel):
    """Validation status for one reader field."""

    field: str
    requirement: FieldRequirement
    present: bool
    value: object | None = None
    message: str | None = None


class ReadValidation(BaseModel):
    """Validation report for one auction read."""

    fields: list[FieldValidation] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return whether all required fields are present."""
        return all(field.present for field in self.fields if field.requirement is FieldRequirement.REQUIRED)

    def missing_required(self) -> list[str]:
        """Return names of missing required fields."""
        return [
            field.field
            for field in self.fields
            if field.requirement is FieldRequirement.REQUIRED and not field.present
        ]


class AuctionReadResult(BaseModel):
    """Result of reading one auction page."""

    car: Car
    snapshot: PageSnapshot
    validation: ReadValidation
    auction_json_path: Path = Field(alias="auctionJsonPath")

    model_config = {"populate_by_name": True}

