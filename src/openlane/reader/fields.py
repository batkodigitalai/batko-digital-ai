"""Field definitions and primitive conversions for the OPENLANE reader."""

from __future__ import annotations

import re

from src.openlane.reader.models import FieldRequirement

DOM_FIELD_ATTRIBUTE = "data-openlane-field"
DOM_FIELD_SELECTOR = f"[{DOM_FIELD_ATTRIBUTE}]"

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


def build_dom_extraction_script() -> str:
    """Return the DOM-only field extraction script used by AuctionReader."""
    return f"""
    () => {{
      const result = {{}};
      document.querySelectorAll('{DOM_FIELD_SELECTOR}').forEach((el) => {{
        const key = el.getAttribute('{DOM_FIELD_ATTRIBUTE}');
        result[key] = (el.getAttribute('content') || el.textContent || '').trim();
      }});
      return result;
    }}
    """


def parse_int(value: object) -> int | None:
    """Parse an integer from display text while preserving empty values as None."""
    if value is None or value == "":
        return None
    digits = re.sub(r"[^\d]", "", str(value))
    return int(digits) if digits else None


def parse_float(value: object) -> float | None:
    """Parse a float from display text while preserving invalid values as None."""
    if value is None or value == "":
        return None
    normalized = re.sub(r"[^\d,.]", "", str(value)).replace(" ", "").replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return None
