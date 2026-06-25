"""OPENLANE page snapshot downloader MVP."""

from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from src.core.download import DownloadManager
from src.core.logging import get_logger
from src.core.storage import ProjectStorage
from src.openlane.downloader.models import PageMetadata, PageSnapshot

logger = get_logger(__name__)


class OpenLaneDownloader:
    """Capture an already-open Playwright page without parsing business data."""

    def __init__(self, storage: ProjectStorage, download_manager: DownloadManager | None = None) -> None:
        self.storage = storage
        self.download_manager = download_manager or DownloadManager(storage=storage)

    def is_openlane_auction_page(self, page) -> bool:
        """Return whether the page appears to be an OPENLANE auction page."""
        metadata = self.get_page_metadata(page)
        url_match = "openlane" in metadata.url.lower() and bool(metadata.auction_id)
        title_match = "openlane" in metadata.title.lower() and bool(metadata.auction_id)
        dom_match = self._get_dom_auction_id(page) is not None
        result = url_match or title_match or dom_match
        logger.info("OPENLANE auction page check for {} -> {}", metadata.url, result)
        return result

    def get_page_metadata(self, page) -> PageMetadata:
        """Return basic metadata for the current page."""
        url = getattr(page, "url", "")
        title = page.title()
        auction_id = self._extract_auction_id(url) or self._get_dom_auction_id(page)
        page_id = self._extract_page_id(url) or auction_id
        metadata = PageMetadata(url=url, title=title, pageId=page_id, auctionId=auction_id)
        logger.info("Captured page metadata title='{}' url='{}'", metadata.title, metadata.url)
        return metadata

    def create_snapshot(self, page, snapshot_id: str | None = None) -> PageSnapshot:
        """Store HTML, title, URL, and full-page screenshot for the current page."""
        metadata = self.get_page_metadata(page)
        resolved_snapshot_id = snapshot_id or metadata.auction_id or str(uuid4())
        snapshot_dir = self._snapshot_directory(resolved_snapshot_id)

        self.download_manager.create_task(
            source=metadata.url,
            target=snapshot_dir / "page.html",
            file_type="html",
            job_id=f"snapshot-{resolved_snapshot_id}",
            metadata={"kind": "page_snapshot"},
        )

        html_path = snapshot_dir / "page.html"
        title_path = snapshot_dir / "page_title.txt"
        url_path = snapshot_dir / "page_url.txt"
        screenshot_path = snapshot_dir / "full_page.png"

        html_path.write_text(page.content(), encoding="utf-8")
        title_path.write_text(metadata.title, encoding="utf-8")
        url_path.write_text(metadata.url, encoding="utf-8")
        page.screenshot(path=str(screenshot_path), full_page=True)

        logger.info("Created page snapshot {}", snapshot_dir)
        return PageSnapshot(
            snapshotId=resolved_snapshot_id,
            directory=snapshot_dir,
            metadata=metadata,
            htmlPath=html_path,
            titlePath=title_path,
            urlPath=url_path,
            screenshotPath=screenshot_path,
        )

    def _snapshot_directory(self, snapshot_id: str) -> Path:
        raw_dir = self.storage.resolve_path(self.storage.config.raw_dir)
        return raw_dir / "openlane" / snapshot_id

    @staticmethod
    def _extract_auction_id(url: str) -> str | None:
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

    @staticmethod
    def _extract_page_id(url: str) -> str | None:
        match = re.search(r"(?:page_id|pageId)=([A-Za-z0-9_-]+)", url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _get_dom_auction_id(page) -> str | None:
        script = """
        () => {
          const direct = document.querySelector('[data-auction-id], [data-openlane-auction-id]');
          if (direct) return direct.getAttribute('data-auction-id') || direct.getAttribute('data-openlane-auction-id');
          const meta = document.querySelector('meta[name="auction-id"], meta[name="openlane-auction-id"]');
          if (meta) return meta.getAttribute('content');
          return null;
        }
        """
        try:
            value = page.evaluate(script)
        except Exception as exc:  # pragma: no cover - defensive for external page handles
            logger.warning("Unable to read auction id from DOM: {}", exc)
            return None
        return str(value) if value else None
