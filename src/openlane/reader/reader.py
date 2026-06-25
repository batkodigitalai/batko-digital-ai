"""DOM-only OPENLANE auction reader."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.core.logging import get_logger
from src.core.storage import build_car_id
from src.domain.models.car import Auction, Car
from src.openlane.downloader import OpenLaneDownloader, PageSnapshot
from src.openlane.reader.models import (
    AuctionReadResult,
    FieldRequirement,
    FieldValidation,
    ReadValidation,
)

logger = get_logger(__name__)


FIELD_REQUIREMENTS: dict[str, FieldRequirement] = {
    "auction_id": FieldRequirement.REQUIRED,
    "reference": FieldRequirement.OPTIONAL,
    "url": FieldRequirement.REQUIRED,
    "title": FieldRequirement.REQUIRED,
    "make": FieldRequirement.REQUIRED,
    "model": FieldRequirement.REQUIRED,
    "variant": FieldRequirement.OPTIONAL,
    "vin": FieldRequirement.OPTIONAL,
    "first_registration": FieldRequirement.OPTIONAL,
    "manufacture_date": FieldRequirement.OPTIONAL,
    "mileage_km": FieldRequirement.REQUIRED,
    "power_kw": FieldRequirement.OPTIONAL,
    "fuel": FieldRequirement.OPTIONAL,
    "transmission": FieldRequirement.OPTIONAL,
    "color": FieldRequirement.OPTIONAL,
    "current_price": FieldRequirement.OPTIONAL,
    "currency": FieldRequirement.OPTIONAL,
    "vat_mode": FieldRequirement.OPTIONAL,
    "country": FieldRequirement.OPTIONAL,
    "location": FieldRequirement.OPTIONAL,
}


class AuctionReader:
    """Read basic vehicle data from an already-open auction page using DOM only."""

    def __init__(self, downloader: OpenLaneDownloader) -> None:
        self.downloader = downloader

    def read_current_auction(self, page, snapshot_id: str | None = None) -> AuctionReadResult:
        """Create a snapshot, read DOM fields, map them to Car, and export JSON."""
        snapshot = self.downloader.create_snapshot(page, snapshot_id=snapshot_id)
        values = self._extract_fields(page, snapshot)
        validation = self._validate(values)
        car = self._map_to_car(values)
        auction_json_path = self._export(snapshot, car, validation)
        logger.info("Read auction {} into {}", car.source_item_id, auction_json_path)
        return AuctionReadResult(
            car=car,
            snapshot=snapshot,
            validation=validation,
            auctionJsonPath=auction_json_path,
        )

    def _extract_fields(self, page, snapshot: PageSnapshot) -> dict[str, Any]:
        dom_values = page.evaluate(
            """
            () => {
              const result = {};
              document.querySelectorAll('[data-openlane-field]').forEach((el) => {
                const key = el.getAttribute('data-openlane-field');
                result[key] = (el.getAttribute('content') || el.textContent || '').trim();
              });
              return result;
            }
            """
        )
        values: dict[str, Any] = dict(dom_values or {})
        values.setdefault("auction_id", snapshot.metadata.auction_id)
        values.setdefault("url", snapshot.metadata.url)
        values.setdefault("title", snapshot.metadata.title)
        values["mileage_km"] = self._parse_int(values.get("mileage_km"))
        values["power_kw"] = self._parse_int(values.get("power_kw"))
        values["current_price"] = self._parse_float(values.get("current_price"))
        return values

    def _validate(self, values: dict[str, Any]) -> ReadValidation:
        fields: list[FieldValidation] = []
        for field, requirement in FIELD_REQUIREMENTS.items():
            value = values.get(field)
            present = value is not None and value != ""
            fields.append(
                FieldValidation(
                    field=field,
                    requirement=requirement,
                    present=present,
                    value=value,
                    message=None if present or requirement is not FieldRequirement.REQUIRED else "Missing required field",
                )
            )
        known_fields = set(FIELD_REQUIREMENTS)
        for field, value in values.items():
            if field not in known_fields:
                fields.append(
                    FieldValidation(
                        field=field,
                        requirement=FieldRequirement.UNKNOWN,
                        present=value is not None and value != "",
                        value=value,
                    )
                )
        return ReadValidation(fields=fields)

    def _map_to_car(self, values: dict[str, Any]) -> Car:
        auction_id = str(values.get("auction_id") or "unknown")
        make = str(values.get("make") or "unknown")
        model = str(values.get("model") or "unknown")
        return Car(
            id=build_car_id("openlane", auction_id),
            source="openlane",
            sourceItemId=auction_id,
            make=make,
            model=model,
            variant=values.get("variant"),
            firstRegistration=values.get("first_registration"),
            manufactureDate=values.get("manufacture_date"),
            mileageKm=values.get("mileage_km"),
            fuel=values.get("fuel"),
            transmission=values.get("transmission"),
            powerKw=values.get("power_kw"),
            color=values.get("color"),
            vin=values.get("vin"),
            auction=Auction(
                platform="openlane",
                itemId=auction_id,
                reference=values.get("reference"),
                url=values.get("url"),
                country=values.get("country"),
                location=values.get("location"),
                currency=values.get("currency"),
                currentBid=values.get("current_price"),
                vatMode=values.get("vat_mode"),
            ),
        )

    @staticmethod
    def _export(snapshot: PageSnapshot, car: Car, validation: ReadValidation) -> Path:
        auction_json_path = snapshot.directory / "auction.json"
        payload = {
            "schemaVersion": "1.0",
            "snapshot": snapshot.model_dump(mode="json", by_alias=True),
            "validation": {
                "isValid": validation.is_valid,
                "missingRequired": validation.missing_required(),
                "fields": [field.model_dump(mode="json") for field in validation.fields],
            },
            "car": car.model_dump(mode="json", by_alias=True),
        }
        auction_json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return auction_json_path

    @staticmethod
    def _parse_int(value: object) -> int | None:
        if value is None or value == "":
            return None
        digits = re.sub(r"[^\d]", "", str(value))
        return int(digits) if digits else None

    @staticmethod
    def _parse_float(value: object) -> float | None:
        if value is None or value == "":
            return None
        normalized = re.sub(r"[^\d,.]", "", str(value)).replace(" ", "").replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return None

