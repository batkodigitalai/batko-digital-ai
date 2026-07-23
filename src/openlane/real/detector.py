"""Detect metadata on a real already-open OPENLANE auction page."""

from __future__ import annotations

import re
from pathlib import Path

from src.core.logging import get_logger
from src.openlane.real.models import OpenLaneAuctionDetectionError, RealAuctionDetection
from src.openlane.real.selectors import SelectorRegistry, SelectorValidator

logger = get_logger(__name__)


class RealAuctionDetector:
    """Detect whether the active page is a real OPENLANE auction page."""

    def __init__(
        self,
        project_root: Path | str = ".",
        selector_version: str = "v1",
        registry: SelectorRegistry | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.selector_version = selector_version
        self.registry = registry or SelectorRegistry(project_root=self.project_root)
        self.validator = SelectorValidator(self.registry)

    def detect(self, page) -> RealAuctionDetection:
        """Return auction metadata or raise a clear user-facing error."""
        selectors = self.registry.get(self.selector_version)
        report = self.validator.validate(page, self.selector_version)
        url = getattr(page, "url", "")
        title = self._read_field(page, "title") or page.title()
        auction_id = self._read_field(page, "auction_id") or self._auction_id_from_url(url)
        reference = self._read_field(page, "reference")

        marker_found = any(check.exists for check in report.checks if check.group == "auctionMarkers")
        url_matches = any(pattern.lower() in url.lower() for pattern in selectors.url_patterns)
        if not marker_found and not url_matches:
            raise OpenLaneAuctionDetectionError(
                "Aktualne otevrena stranka nevypada jako aukce OPENLANE. "
                "Otevri detail aukce v prihlasenem Chromu a spust detekci znovu."
            )
        if not auction_id:
            raise OpenLaneAuctionDetectionError(
                "Aukce OPENLANE byla rozpoznana, ale nepodarilo se zjistit auction_id. "
                "Zkontroluj Selector Registry pro aktualni verzi OPENLANE."
            )

        result = RealAuctionDetection(
            title=title,
            auctionId=auction_id,
            reference=reference,
            url=url,
            selectorVersion=self.selector_version,
            selectorReport=report,
        )
        logger.info(
            "Detected OPENLANE auction title='{}' auction_id='{}' reference='{}' url='{}'",
            result.title,
            result.auction_id,
            result.reference,
            result.url,
        )
        return result

    def _read_field(self, page, field: str) -> str | None:
        selectors = self.registry.get(self.selector_version).fields.get(field, [])
        for selector in selectors:
            value = self._read_selector(page, selector)
            if value:
                return value
        return None

    @staticmethod
    def _read_selector(page, selector: str) -> str | None:
        script = """
        (selector) => {
          const el = document.querySelector(selector);
          if (!el) return null;
          const attributes = ['content', 'data-openlane-auction-id', 'data-auction-id', 'data-reference', 'data-auction-reference', 'data-item-id'];
          for (const attribute of attributes) {
            const value = el.getAttribute(attribute);
            if (value && value.trim()) return value.trim();
          }
          const text = el.textContent || '';
          return text.trim() || null;
        }
        """
        try:
            value = page.evaluate(script, selector)
        except Exception:
            return None
        return str(value).strip() if value else None

    @staticmethod
    def _auction_id_from_url(url: str) -> str | None:
        patterns = [
            r"/item/(\d+)",
            r"[?&](?:auction_id|auctionId|item|id)=(\d+)",
            r"/(\d{6,})(?:[/?#]|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
