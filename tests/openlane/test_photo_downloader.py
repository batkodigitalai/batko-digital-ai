import json
from pathlib import Path

import pytest

from src.core.download import calculate_sha256
from src.openlane.capture import CaptureService


def test_capture_service_downloads_gallery_photos(tmp_path: Path) -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "openlane_photo_gallery.html"
    capture_dir = tmp_path / "photo-capture"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.as_uri())

            result = CaptureService(project_root=tmp_path).capture(page, output_dir=capture_dir)

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise

    photos_dir = capture_dir / "02_Photos"
    assert photos_dir.exists()
    assert (photos_dir / "001.jpg").read_bytes() == b"photo-001"
    assert (photos_dir / "002.jpg").read_bytes() == b"photo-002"
    assert (photos_dir / "003.jpg").read_bytes() == b"photo-003"
    assert not (photos_dir / "004.jpg").exists()

    photos_payload = json.loads((photos_dir / "photos.json").read_text(encoding="utf-8"))
    assert photos_payload["total"] == 4
    assert photos_payload["downloaded"] == 3
    assert photos_payload["failed"] == 1
    assert [photo["localFile"] for photo in photos_payload["photos"]] == ["001.jpg", "002.jpg", "003.jpg", "004.jpg"]
    for photo in photos_payload["photos"][:3]:
        file_path = photos_dir / photo["localFile"]
        assert photo["result"] == "SUCCESS"
        assert photo["sha256"] == calculate_sha256(file_path)
        assert photo["sizeBytes"] == file_path.stat().st_size
    assert photos_payload["photos"][3]["result"] == "FAILED"
    assert photos_payload["photos"][3]["sha256"] is None
    assert photos_payload["photos"][3]["sizeBytes"] is None

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["photoTotal"] == 4
    assert manifest["photoDownloaded"] == 3
    assert manifest["photoFailed"] == 1
    manifest_files = {entry["path"]: entry for entry in manifest["files"]}
    for relative_path in ["02_Photos/photos.json", "02_Photos/001.jpg", "02_Photos/002.jpg", "02_Photos/003.jpg"]:
        assert relative_path in manifest_files
        assert manifest_files[relative_path]["sha256"] == calculate_sha256(capture_dir / relative_path)
