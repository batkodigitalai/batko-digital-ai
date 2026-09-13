"""Pydantic domain models from CAR_DATA_MODEL.md."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl


class Auction(BaseModel):
    """Auction metadata for a vehicle source listing."""

    platform: str
    item_id: str = Field(alias="itemId")
    reference: str | None = None
    url: str | None = None
    country: str | None = None
    location: str | None = None
    currency: str | None = None
    current_bid: float | None = Field(default=None, alias="currentBid")
    vat_mode: str | None = Field(default=None, alias="vatMode")
    auction_end_at: datetime | None = Field(default=None, alias="auctionEndAt")

    model_config = {"populate_by_name": True}


class Condition(BaseModel):
    """Vehicle condition metadata without business scoring logic."""

    damage_summary: str | None = Field(default=None, alias="damageSummary")
    service_history: str | None = Field(default=None, alias="serviceHistory")
    documents_available: bool | None = Field(default=None, alias="documentsAvailable")
    risk_notes: list[str] = Field(default_factory=list, alias="riskNotes")

    model_config = {"populate_by_name": True}


class Asset(BaseModel):
    """Vehicle asset reference."""

    id: str
    type: str
    path: Path | None = None
    original_source_url: HttpUrl | None = Field(default=None, alias="originalSourceUrl")
    role: str | None = None
    alt_text: str | None = Field(default=None, alias="altText")

    model_config = {"populate_by_name": True}


class Document(BaseModel):
    """Vehicle document reference."""

    id: str
    type: str
    path: Path | None = None
    title: str | None = None


class Publication(BaseModel):
    """Publication metadata for generated or future public outputs."""

    status: str = "draft"
    canonical_path: Path | None = Field(default=None, alias="canonicalPath")
    generated_at: datetime | None = Field(default=None, alias="generatedAt")
    page_types: list[str] = Field(default_factory=list, alias="pageTypes")

    model_config = {"populate_by_name": True}


class Car(BaseModel):
    """Normalized vehicle record."""

    id: str
    source: str
    source_item_id: str | None = Field(default=None, alias="sourceItemId")
    make: str
    model: str
    variant: str | None = None
    year: int | None = None
    first_registration: str | None = Field(default=None, alias="firstRegistration")
    manufacture_date: str | None = Field(default=None, alias="manufactureDate")
    mileage_km: int | None = Field(default=None, alias="mileageKm")
    fuel: str | None = None
    transmission: str | None = None
    power_kw: int | None = Field(default=None, alias="powerKw")
    color: str | None = None
    vin: str | None = None
    auction: Auction | None = None
    condition: Condition | None = None
    pricing: dict[str, object] = Field(default_factory=dict)
    assets: list[Asset] = Field(default_factory=list)
    documents: list[Document] = Field(default_factory=list)
    publication: Publication = Field(default_factory=Publication)

    model_config = {"populate_by_name": True}
