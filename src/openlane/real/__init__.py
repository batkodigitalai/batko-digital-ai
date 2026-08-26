"""Real OPENLANE page detection and selector compatibility."""

from src.openlane.real.detector import RealAuctionDetector
from src.openlane.real.models import (
    OpenLaneAuctionDetectionError,
    RealAuctionDetection,
    SelectorCheck,
    SelectorConfig,
    SelectorValidationReport,
    SelectorVersion,
)
from src.openlane.real.selectors import SelectorRegistry, SelectorValidator

__all__ = [
    "OpenLaneAuctionDetectionError",
    "RealAuctionDetection",
    "RealAuctionDetector",
    "SelectorCheck",
    "SelectorConfig",
    "SelectorRegistry",
    "SelectorValidationReport",
    "SelectorValidator",
    "SelectorVersion",
]
