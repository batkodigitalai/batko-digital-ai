"""Naming helpers based on NAMING_STANDARD.md."""

from __future__ import annotations

import re

from src.core.logging import get_logger

logger = get_logger(__name__)


def normalize_slug(value: str) -> str:
    """Normalize a value for stable file-system paths."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    normalized = re.sub(r"_+", "_", slug)
    logger.debug("Normalized slug '{}' -> '{}'", value, normalized)
    return normalized or "unknown"


def build_car_id(source: str, item_id: str) -> str:
    """Build a stable car identifier from source and item id."""
    car_id = f"{normalize_slug(source)}_{normalize_slug(item_id)}"
    logger.debug("Built car id {}", car_id)
    return car_id

