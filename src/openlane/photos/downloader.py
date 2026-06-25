"""Download OPENLANE gallery photos into a capture archive."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from src.core.download import DownloadManager, calculate_sha256
from src.core.logging import get_logger
from src.openlane.photos.collector import PhotoCollector
from src.openlane.photos.models import PhotoDownloadStatus, PhotoManifest, PhotoManifestItem

logger = get_logger(__name__)


class PhotoDownloader:
    """Download gallery photos and write photos.json."""

    def __init__(self, download_manager: DownloadManager, collector: PhotoCollector | None = None) -> None:
        self.download_manager = download_manager
        self.collector = collector or PhotoCollector()

    def download(self, page, photos_dir: Path | str) -> PhotoManifest:
        """Collect and download photos into numbered JPG files."""
        target_dir = Path(photos_dir)
        urls = self.collector.collect(page)
        if not urls:
            logger.info("No gallery photos found")
            return PhotoManifest(total=0, downloaded=0, failed=0)

        target_dir.mkdir(parents=True, exist_ok=True)
        items: list[PhotoManifestItem] = []
        for order, url in enumerate(urls, start=1):
            target = target_dir / f"{order:03d}.jpg"
            self.download_manager.create_task(
                source=url,
                target=target,
                file_type="image",
                job_id=f"photo-{order:03d}",
                metadata={"kind": "auction_photo"},
            )
            item = self._download_one(page, order, url, target)
            items.append(item)

        manifest = PhotoManifest(
            total=len(items),
            downloaded=sum(1 for item in items if item.result is PhotoDownloadStatus.SUCCESS),
            failed=sum(1 for item in items if item.result is PhotoDownloadStatus.FAILED),
            photos=items,
        )
        (target_dir / "photos.json").write_text(
            json.dumps(manifest.model_dump(mode="json", by_alias=True), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        logger.info("Downloaded {}/{} gallery photos", manifest.downloaded, manifest.total)
        return manifest

    def _download_one(self, page, order: int, url: str, target: Path) -> PhotoManifestItem:
        try:
            content = self._read_url(page, url)
            target.write_bytes(content)
            return PhotoManifestItem(
                order=order,
                url=url,
                localFile=target.name,
                sha256=calculate_sha256(target),
                sizeBytes=target.stat().st_size,
                result=PhotoDownloadStatus.SUCCESS,
            )
        except Exception as exc:
            logger.warning("Unable to download photo {}: {}", url, exc)
            return PhotoManifestItem(
                order=order,
                url=url,
                localFile=target.name,
                result=PhotoDownloadStatus.FAILED,
                error=str(exc),
            )

    def _read_url(self, page, url: str) -> bytes:
        parsed = urlparse(url)
        if parsed.scheme == "file":
            return Path(url2pathname(unquote(parsed.path))).read_bytes()
        if parsed.scheme == "data":
            return self._read_data_url(url)
        return self._read_with_playwright(page, url)

    @staticmethod
    def _read_data_url(url: str) -> bytes:
        header, payload = url.split(",", 1)
        if ";base64" in header:
            return base64.b64decode(payload, validate=True)
        return unquote(payload).encode("utf-8")

    @staticmethod
    def _read_with_playwright(page, url: str) -> bytes:
        context = getattr(page, "context", None)
        request_context = getattr(context, "request", None)
        if request_context is None:
            raise RuntimeError("Playwright request context is not available")
        response = request_context.get(url)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status}")
        return response.body()
