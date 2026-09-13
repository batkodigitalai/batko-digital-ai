"""End-to-end OPENLANE auction capture service."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src import __version__
from src.core.config.models import StorageConfig
from src.core.download import DownloadManager, calculate_sha256
from src.core.logging import get_logger
from src.core.storage import ProjectStorage, build_car_id
from src.openlane.downloader import OpenLaneDownloader
from src.openlane.photos import PhotoDownloader, PhotoDownloadStatus, PhotoManifest
from src.openlane.reader import AuctionReader
from src.openlane.capture.models import CaptureManifest, CaptureResult, CaptureStatus, ManifestFile

logger = get_logger(__name__)


class _CaptureStorage(ProjectStorage):
    """Storage adapter that prepares only capture targets, not project-level folders."""

    def ensure_project_directories(self) -> list[Path]:
        return []


class CaptureService:
    """Orchestrate a complete archive capture for the active auction page."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def capture(self, page, output_dir: Path | str | None = None) -> CaptureResult:
        """Capture the active auction page into a self-contained archive directory."""
        capture_dir = self._prepare_capture_dir(page, output_dir)
        source_dir = capture_dir / "01_Source"
        work_dir = capture_dir / "_work"
        source_dir.mkdir(parents=True, exist_ok=True)
        work_dir.mkdir(parents=True, exist_ok=True)

        storage = _CaptureStorage(project_root=capture_dir, config=StorageConfig(raw_dir=Path("_work")))
        download_manager = DownloadManager(storage=storage)
        reader = AuctionReader(downloader=OpenLaneDownloader(storage=storage, download_manager=download_manager))
        read_result = reader.read_current_auction(page, snapshot_id="capture")

        self._copy_snapshot_files(read_result, source_dir)
        self._rewrite_auction_snapshot_paths(source_dir / "auction.json", source_dir)
        photos_dir = capture_dir / "02_Photos"
        photo_manifest = PhotoDownloader(download_manager=download_manager).download(page, photos_dir)
        if photo_manifest.total == 0:
            photo_manifest = None
        log_path = self._write_capture_log(source_dir, read_result)
        manifest = self._build_manifest(source_dir, read_result, log_path, photo_manifest, photos_dir)
        manifest_path = source_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest.model_dump(mode="json", by_alias=True), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        shutil.rmtree(work_dir)
        logger.info("Created OPENLANE capture archive {}", source_dir)
        return CaptureResult(
            captureDir=capture_dir,
            sourceDir=source_dir,
            manifestPath=manifest_path,
            logPath=log_path,
            manifest=manifest,
            readResult=read_result,
            photoManifest=photo_manifest,
        )

    def _prepare_capture_dir(self, page, output_dir: Path | str | None) -> Path:
        if output_dir is not None:
            capture_dir = Path(output_dir)
            capture_dir.mkdir(parents=True, exist_ok=True)
            return capture_dir

        metadata = OpenLaneDownloader(storage=ProjectStorage(project_root=self.project_root)).get_page_metadata(page)
        auction_id = metadata.auction_id or "unknown"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        capture_id = build_car_id("openlane", f"{auction_id}_{timestamp}")
        capture_dir = self.project_root / "30_DATA" / "raw" / "openlane" / "captures" / capture_id
        capture_dir.mkdir(parents=True, exist_ok=True)
        return capture_dir

    @staticmethod
    def _copy_snapshot_files(read_result, source_dir: Path) -> None:
        snapshot = read_result.snapshot
        files = [
            (snapshot.html_path, source_dir / "page.html"),
            (snapshot.url_path, source_dir / "page_url.txt"),
            (snapshot.title_path, source_dir / "page_title.txt"),
            (snapshot.screenshot_path, source_dir / "full_page.png"),
            (read_result.auction_json_path, source_dir / "auction.json"),
        ]
        for source, target in files:
            shutil.copy2(source, target)

    @staticmethod
    def _rewrite_auction_snapshot_paths(auction_json_path: Path, source_dir: Path) -> None:
        payload = json.loads(auction_json_path.read_text(encoding="utf-8"))
        snapshot = payload.get("snapshot", {})
        snapshot["directory"] = str(source_dir)
        snapshot["htmlPath"] = str(source_dir / "page.html")
        snapshot["titlePath"] = str(source_dir / "page_title.txt")
        snapshot["urlPath"] = str(source_dir / "page_url.txt")
        snapshot["screenshotPath"] = str(source_dir / "full_page.png")
        payload["snapshot"] = snapshot
        auction_json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def _write_capture_log(source_dir: Path, read_result) -> Path:
        log_path = source_dir / "capture.log"
        status = CaptureStatus.SUCCESS if read_result.validation.is_valid else CaptureStatus.PARTIAL
        lines = [
            f"captured_at={datetime.now(timezone.utc).isoformat()}",
            f"status={status.value}",
            f"auction_id={read_result.car.source_item_id}",
            f"url={read_result.snapshot.metadata.url}",
            f"missing_required={','.join(read_result.validation.missing_required())}",
        ]
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return log_path

    def _build_manifest(
        self,
        source_dir: Path,
        read_result,
        log_path: Path,
        photo_manifest: PhotoManifest | None = None,
        photos_dir: Path | None = None,
    ) -> CaptureManifest:
        files = [
            self._manifest_file(source_dir, source_dir / "page.html"),
            self._manifest_file(source_dir, source_dir / "page_url.txt"),
            self._manifest_file(source_dir, source_dir / "page_title.txt"),
            self._manifest_file(source_dir, source_dir / "auction.json"),
            self._manifest_file(source_dir, log_path),
            self._manifest_file(source_dir, source_dir / "full_page.png"),
        ]
        if photo_manifest is not None and photos_dir is not None:
            files.append(self._manifest_file(source_dir.parent, photos_dir / "photos.json"))
            for photo in photo_manifest.photos:
                if photo.result is PhotoDownloadStatus.SUCCESS and photo.local_file:
                    files.append(self._manifest_file(source_dir.parent, photos_dir / photo.local_file))
        status = CaptureStatus.SUCCESS if read_result.validation.is_valid else CaptureStatus.PARTIAL
        return CaptureManifest(
            capturedAt=datetime.now(timezone.utc),
            appVersion=__version__,
            commitHash=self._commit_hash(),
            status=status,
            url=read_result.snapshot.metadata.url,
            auctionId=read_result.car.source_item_id,
            files=files,
            missingRequired=read_result.validation.missing_required(),
            photoTotal=photo_manifest.total if photo_manifest else 0,
            photoDownloaded=photo_manifest.downloaded if photo_manifest else 0,
            photoFailed=photo_manifest.failed if photo_manifest else 0,
        )

    @staticmethod
    def _manifest_file(source_dir: Path, path: Path) -> ManifestFile:
        return ManifestFile(
            path=path.relative_to(source_dir).as_posix(),
            sha256=calculate_sha256(path),
            sizeBytes=path.stat().st_size,
        )

    def _commit_hash(self) -> str | None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception:
            return None
        commit_hash = result.stdout.strip()
        return commit_hash or None
